import * as THREE from
    "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";


/* =========================================================
   HANNAH ENERGY CORE
   ========================================================= */

const orbContainer =
    document.getElementById("orb-container");


if (!orbContainer) {

    console.error(
        "orb-container was not found."
    );

} else {


    /* =====================================================
       COLORS
       ===================================================== */

    const ORANGE =
        0xff5a00;

    const BRIGHT_ORANGE =
        0xff8a00;

    const HOT_ORANGE =
        0xffb52e;

    const CORE_WHITE =
        0xffffee;


    /* =====================================================
       SCENE
       ===================================================== */

    const scene =
        new THREE.Scene();


    /* =====================================================
       CAMERA
       ===================================================== */

    const camera =
        new THREE.PerspectiveCamera(
            45,
            1,
            0.1,
            100
        );


    /*
     * Slightly farther initial position.
     * This gives the orb room to expand.
     */

    camera.position.z =
        4.55;


    /* =====================================================
       RENDERER
       ===================================================== */

    const renderer =
        new THREE.WebGLRenderer({

            antialias: true,

            alpha: true,

            powerPreference:
                "high-performance"

        });


    renderer.setPixelRatio(
        Math.min(
            window.devicePixelRatio,
            2
        )
    );


    renderer.setClearColor(
        0x000000,
        0
    );


    renderer.domElement.style.display =
        "block";


    renderer.domElement.style.width =
        "100%";


    renderer.domElement.style.height =
        "100%";


    orbContainer.appendChild(
        renderer.domElement
    );


    /* =====================================================
       RESIZE
       ===================================================== */

    function resizeRenderer() {

        const width =
            orbContainer.clientWidth;

        const height =
            orbContainer.clientHeight;


        if (
            width <= 0 ||
            height <= 0
        ) {

            return;

        }


        camera.aspect =
            width / height;


        camera.updateProjectionMatrix();


        renderer.setSize(
            width,
            height,
            false
        );

    }


    resizeRenderer();


    window.addEventListener(
        "resize",
        resizeRenderer
    );


    if (
        window.ResizeObserver
    ) {

        const resizeObserver =
            new ResizeObserver(
                () => {

                    resizeRenderer();

                }
            );


        resizeObserver.observe(
            orbContainer
        );

    }


    /* =====================================================
       AUDIO
       ===================================================== */

    let audioContext =
        null;

    let analyser =
        null;

    let audioData =
        null;

    let audioLevel =
        0;

    let targetAudioLevel =
        0;


    /* =====================================================
       HANNAH STATE
       ===================================================== */

    let hannahState =
        "idle";


    /*
     * States:
     *
     * idle
     * listening
     * thinking
     * speaking
     */

    function setHannahState(
        state
    ) {

        const value =
            String(
                state || ""
            ).toLowerCase();


        if (
            value.includes("listen")
        ) {

            hannahState =
                "listening";

            return;

        }


        if (
            value.includes("speak")
        ) {

            hannahState =
                "speaking";

            return;

        }


        if (
            value.includes("understand") ||
            value.includes("prepar") ||
            value.includes("process") ||
            value.includes("using") ||
            value.includes("think")
        ) {

            hannahState =
                "thinking";

            return;

        }


        hannahState =
            "idle";

    }


    window.setHannahOrbState =
        setHannahState;


    /* =====================================================
       WATCH STATUS
       ===================================================== */

    const statusElement =
        document.getElementById(
            "status"
        );


    if (statusElement) {

        function updateStateFromStatus() {

            setHannahState(
                statusElement.textContent
            );

        }


        updateStateFromStatus();


        if (
            window.MutationObserver
        ) {

            const statusObserver =
                new MutationObserver(
                    () => {

                        updateStateFromStatus();

                    }
                );


            statusObserver.observe(
                statusElement,
                {
                    childList: true,
                    characterData: true,
                    subtree: true
                }
            );

        }

    }


    /* =====================================================
       LIQUID CORE SHADER
       ===================================================== */

    const coreGeometry =
        new THREE.IcosahedronGeometry(
            1,
            32
        );


    const coreMaterial =
        new THREE.ShaderMaterial({

            transparent:
                true,

            depthWrite:
                false,

            uniforms: {

                uTime: {
                    value: 0
                },

                uAudio: {
                    value: 0
                },

                uState: {
                    value: 0
                }

            },


            vertexShader: `

                uniform float uTime;
                uniform float uAudio;
                uniform float uState;

                varying vec3 vNormal;
                varying vec3 vPosition;


                float wave(vec3 p) {

                    float w1 =
                        sin(
                            p.x * 4.0 +
                            uTime * 1.7
                        );

                    float w2 =
                        sin(
                            p.y * 5.0 -
                            uTime * 1.3
                        );

                    float w3 =
                        sin(
                            p.z * 6.0 +
                            uTime * 1.9
                        );

                    float w4 =
                        sin(
                            (
                                p.x +
                                p.y +
                                p.z
                            ) * 7.0 -
                            uTime * 1.1
                        );

                    return (
                        w1 +
                        w2 +
                        w3 +
                        w4
                    ) * 0.25;

                }


                void main() {

                    vec3 pos =
                        position;


                    float baseWave =
                        wave(
                            normalize(pos)
                        );


                    float stateEnergy =
                        0.12 +
                        uState * 0.22;


                    float audioEnergy =
                        uAudio * 0.55;


                    float displacement =
                        (
                            baseWave *
                            stateEnergy
                        )
                        +
                        audioEnergy;


                    vec3 direction =
                        normalize(pos);


                    pos +=
                        direction *
                        displacement;


                    float pulse =
                        sin(
                            uTime * 8.0
                        ) *
                        uAudio *
                        0.045;


                    pos +=
                        direction *
                        pulse;


                    vNormal =
                        normalize(
                            normalMatrix *
                            normal
                        );


                    vPosition =
                        pos;


                    gl_Position =
                        projectionMatrix *
                        modelViewMatrix *
                        vec4(
                            pos,
                            1.0
                        );

                }

            `,


            fragmentShader: `

                uniform float uTime;
                uniform float uAudio;
                uniform float uState;

                varying vec3 vNormal;
                varying vec3 vPosition;


                void main() {

                    vec3 viewDirection =
                        normalize(
                            cameraPosition -
                            vPosition
                        );


                    float fresnel =
                        pow(
                            1.0 -
                            max(
                                dot(
                                    vNormal,
                                    viewDirection
                                ),
                                0.0
                            ),
                            2.4
                        );


                    float intensity =
                        0.35 +
                        fresnel * 0.75 +
                        uAudio * 0.65;


                    vec3 orange =
                        vec3(
                            1.0,
                            0.35,
                            0.015
                        );


                    vec3 brightOrange =
                        vec3(
                            1.0,
                            0.65,
                            0.18
                        );


                    vec3 color =
                        mix(
                            orange,
                            brightOrange,
                            fresnel +
                            uAudio * 0.35
                        );


                    color *=
                        intensity;


                    float alpha =
                        0.42 +
                        fresnel * 0.42 +
                        uAudio * 0.25;


                    gl_FragColor =
                        vec4(
                            color,
                            alpha
                        );

                }

            `

        });


    const liquidCore =
        new THREE.Mesh(
            coreGeometry,
            coreMaterial
        );


    scene.add(
        liquidCore
    );


    /* =====================================================
       INNER WHITE CORE
       ===================================================== */

    const innerGeometry =
        new THREE.SphereGeometry(
            0.30,
            48,
            48
        );


    const innerMaterial =
        new THREE.MeshBasicMaterial({

            color:
                CORE_WHITE,

            transparent:
                true,

            opacity:
                0.78,

            depthWrite:
                false

        });


    const innerCore =
        new THREE.Mesh(
            innerGeometry,
            innerMaterial
        );


    scene.add(
        innerCore
    );


    /* =====================================================
       ORANGE INNER CORE
       ===================================================== */

    const orangeGeometry =
        new THREE.SphereGeometry(
            0.18,
            32,
            32
        );


    const orangeMaterial =
        new THREE.MeshBasicMaterial({

            color:
                BRIGHT_ORANGE,

            transparent:
                true,

            opacity:
                0.75,

            depthWrite:
                false

        });


    const orangeCore =
        new THREE.Mesh(
            orangeGeometry,
            orangeMaterial
        );


    scene.add(
        orangeCore
    );


    /* =====================================================
       ENERGY RING
       ===================================================== */

    const ringGeometry =
        new THREE.TorusGeometry(
            1.35,
            0.012,
            12,
            160
        );


    const ringMaterial =
        new THREE.MeshBasicMaterial({

            color:
                ORANGE,

            transparent:
                true,

            opacity:
                0.38,

            depthWrite:
                false

        });


    const ring =
        new THREE.Mesh(
            ringGeometry,
            ringMaterial
        );


    ring.rotation.x =
        Math.PI * 0.35;


    scene.add(
        ring
    );


    /* =====================================================
       SECOND ENERGY RING
       ===================================================== */

    const ring2Geometry =
        new THREE.TorusGeometry(
            1.48,
            0.008,
            10,
            160
        );


    const ring2Material =
        new THREE.MeshBasicMaterial({

            color:
                BRIGHT_ORANGE,

            transparent:
                true,

            opacity:
                0.18,

            depthWrite:
                false

        });


    const ring2 =
        new THREE.Mesh(
            ring2Geometry,
            ring2Material
        );


    ring2.rotation.y =
        Math.PI * 0.55;


    ring2.rotation.x =
        Math.PI * 0.18;


    scene.add(
        ring2
    );


    /* =====================================================
       PARTICLES
       ===================================================== */

    const particleCount =
        900;


    const particlePositions =
        new Float32Array(
            particleCount * 3
        );


    const particleSizes =
        new Float32Array(
            particleCount
        );


    for (
        let i = 0;
        i < particleCount;
        i++
    ) {

        const i3 =
            i * 3;


        const angle =
            Math.random() *
            Math.PI *
            2;


        const radius =
            1.55 +
            Math.random() *
            0.85;


        particlePositions[i3] =
            Math.cos(angle) *
            radius;


        particlePositions[i3 + 1] =
            (
                Math.random() -
                0.5
            ) *
            1.7;


        particlePositions[i3 + 2] =
            Math.sin(angle) *
            radius;


        particleSizes[i] =
            0.025 +
            Math.random() *
            0.045;

    }


    const particleGeometry =
        new THREE.BufferGeometry();


    particleGeometry.setAttribute(
        "position",
        new THREE.BufferAttribute(
            particlePositions,
            3
        )
    );


    particleGeometry.setAttribute(
        "size",
        new THREE.BufferAttribute(
            particleSizes,
            1
        )
    );


    const particleMaterial =
        new THREE.PointsMaterial({

            color:
                BRIGHT_ORANGE,

            size:
                0.035,

            transparent:
                true,

            opacity:
                0.55,

            depthWrite:
                false,

            blending:
                THREE.AdditiveBlending

        });


    const particles =
        new THREE.Points(
            particleGeometry,
            particleMaterial
        );


    scene.add(
        particles
    );


    /* =====================================================
       AUDIO INITIALIZATION
       ===================================================== */

    function initializeAudio() {

        if (audioContext) {

            if (
                audioContext.state ===
                "suspended"
            ) {

                audioContext.resume();

            }

            return;

        }


        audioContext =
            new AudioContext();


        analyser =
            audioContext.createAnalyser();


        analyser.fftSize =
            512;


        analyser.smoothingTimeConstant =
            0.72;


        audioData =
            new Uint8Array(
                analyser.frequencyBinCount
            );


        console.log(
            "Hannah audio system initialized."
        );

    }


    /* =====================================================
       CONNECT AUDIO
       ===================================================== */

    function connectAudio(
        audio
    ) {

        if (!audio) {

            console.error(
                "No audio element supplied to Hannah orb."
            );

            return;

        }


        initializeAudio();


        if (
            audioContext.state ===
            "suspended"
        ) {

            audioContext.resume();

        }


        try {

            const source =
                audioContext.createMediaElementSource(
                    audio
                );


            source.connect(
                analyser
            );


            analyser.connect(
                audioContext.destination
            );


            console.log(
                "Hannah orb connected to audio."
            );

        } catch (error) {

            console.error(
                "Hannah audio connection failed:",
                error
            );

        }

    }


    /* =====================================================
       AUDIO ANALYSIS
       ===================================================== */

    function updateAudioLevel() {

        if (
            !analyser ||
            !audioData
        ) {

            targetAudioLevel =
                0;


            audioLevel +=
                (
                    targetAudioLevel -
                    audioLevel
                ) * 0.08;


            return;

        }


        analyser.getByteFrequencyData(
            audioData
        );


        let total =
            0;


        let weightedTotal =
            0;


        const length =
            audioData.length;


        for (
            let i = 0;
            i < length;
            i++
        ) {

            const frequency =
                i / length;


            let weight =
                0.6;


            if (
                frequency > 0.08 &&
                frequency < 0.65
            ) {

                weight =
                    1.7;

            }


            total +=
                audioData[i];


            weightedTotal +=
                audioData[i] *
                weight;

        }


        const average =
            total /
            length;


        const weightedAverage =
            weightedTotal /
            length;


        targetAudioLevel =
            Math.min(
                (
                    weightedAverage * 0.75 +
                    average * 0.25
                ) / 150,
                1
            );


        if (
            targetAudioLevel >
            audioLevel
        ) {

            audioLevel +=
                (
                    targetAudioLevel -
                    audioLevel
                ) * 0.45;

        } else {

            audioLevel +=
                (
                    targetAudioLevel -
                    audioLevel
                ) * 0.16;

        }

    }


    /* =====================================================
       STATE ENERGY
       ===================================================== */

    function getStateEnergy() {

        if (
            hannahState ===
            "listening"
        ) {

            return 0.75;

        }


        if (
            hannahState ===
            "thinking"
        ) {

            return 0.38;

        }


        if (
            hannahState ===
            "speaking"
        ) {

            return 1.0;

        }


        return 0.12;

    }


    /* =====================================================
       ANIMATION
       ===================================================== */

    const clock =
        new THREE.Clock();


    let elapsedTime =
        0;


    function animate() {

        requestAnimationFrame(
            animate
        );


        const delta =
            Math.min(
                clock.getDelta(),
                0.05
            );


        elapsedTime +=
            delta;


        updateAudioLevel();


        const stateEnergy =
            getStateEnergy();


        const visualEnergy =
            Math.max(
                stateEnergy,
                audioLevel
            );


        /* =================================================
           DYNAMIC CAMERA FRAMING
           ================================================= */

        /*
         * When Hannah speaks, the orb expands.
         *
         * Instead of allowing the expanded orb
         * to touch the canvas edges, smoothly
         * move the camera backward.
         */

        const targetCameraZ =
            4.55 +
            audioLevel * 0.90 +
            stateEnergy * 0.15;


        camera.position.z +=
            (
                targetCameraZ -
                camera.position.z
            ) * 0.10;


        /* =================================================
           LIQUID CORE
           ================================================= */

        coreMaterial.uniforms.uTime.value =
            elapsedTime;


        coreMaterial.uniforms.uAudio.value =
            audioLevel;


        coreMaterial.uniforms.uState.value =
            stateEnergy;


        const rotationSpeed =
            0.12 +
            visualEnergy * 0.55;


        liquidCore.rotation.x +=
            delta *
            rotationSpeed *
            0.45;


        liquidCore.rotation.y +=
            delta *
            rotationSpeed;


        liquidCore.rotation.z +=
            delta *
            rotationSpeed *
            0.18;


        /* =================================================
           CORE SCALE
           ================================================= */

        const coreScale =
            1.0 +
            audioLevel * 0.22 +
            stateEnergy * 0.035;


        liquidCore.scale.set(
            coreScale,
            coreScale,
            coreScale
        );


        /* =================================================
           INNER CORE
           ================================================= */

        const innerScale =
            1.0 +
            audioLevel * 1.4 +
            stateEnergy * 0.12;


        innerCore.scale.set(
            innerScale,
            innerScale,
            innerScale
        );


        innerCore.position.y =
            Math.sin(
                elapsedTime * 2.5
            ) *
            (
                0.008 +
                visualEnergy * 0.025
            );


        innerMaterial.opacity =
            0.62 +
            audioLevel * 0.30;


        /* =================================================
           ORANGE CORE
           ================================================= */

        const orangeScale =
            1.0 +
            audioLevel * 2.2;


        orangeCore.scale.set(
            orangeScale,
            orangeScale,
            orangeScale
        );


        orangeCore.position.y =
            Math.sin(
                elapsedTime * 4
            ) *
            (
                0.008 +
                audioLevel * 0.02
            );


        orangeMaterial.opacity =
            0.48 +
            audioLevel * 0.42;


        /* =================================================
           ENERGY RINGS
           ================================================= */

        ring.rotation.z +=
            delta *
            (
                0.25 +
                visualEnergy * 1.2
            );


        ring.rotation.x =
            Math.PI * 0.35 +
            Math.sin(
                elapsedTime * 0.8
            ) *
            0.12;


        const ringScale =
            1.0 +
            audioLevel * 0.45 +
            stateEnergy * 0.08;


        ring.scale.set(
            ringScale,
            ringScale,
            ringScale
        );


        ringMaterial.opacity =
            0.22 +
            audioLevel * 0.58;


        ring2.rotation.y -=
            delta *
            (
                0.18 +
                visualEnergy * 0.9
            );


        ring2.rotation.x =
            Math.PI * 0.18 +
            Math.sin(
                elapsedTime * 0.65
            ) *
            0.18;


        const ring2Scale =
            1.0 +
            audioLevel * 0.65;


        ring2.scale.set(
            ring2Scale,
            ring2Scale,
            ring2Scale
        );


        ring2Material.opacity =
            0.10 +
            audioLevel * 0.35;


        /* =================================================
           PARTICLES
           ================================================= */

        particles.rotation.y +=
            delta *
            (
                0.08 +
                visualEnergy * 0.45
            );


        particles.rotation.x =
            Math.sin(
                elapsedTime * 0.25
            ) *
            0.08;


        const particleScale =
            1.0 +
            audioLevel * 0.45 +
            stateEnergy * 0.12;


        particles.scale.set(
            particleScale,
            particleScale,
            particleScale
        );


        particleMaterial.opacity =
            0.30 +
            audioLevel * 0.65 +
            stateEnergy * 0.15;


        /* =================================================
           ACTIVE FLOATING
           ================================================= */

        const floatAmount =
            0.008 +
            visualEnergy * 0.035;


        liquidCore.position.y =
            Math.sin(
                elapsedTime * 1.8
            ) *
            floatAmount;


        liquidCore.position.x =
            Math.sin(
                elapsedTime * 1.15
            ) *
            (
                floatAmount * 0.45
            );


        /* =================================================
           RENDER
           ================================================= */

        renderer.render(
            scene,
            camera
        );

    }


    /* =====================================================
       START
       ===================================================== */

    animate();


    /* =====================================================
       GLOBAL API
       ===================================================== */

    window.initializeOrbAudio =
        initializeAudio;


    window.connectOrbToAudio =
        connectAudio;


    window.resizeHannahOrb =
        resizeRenderer;

}