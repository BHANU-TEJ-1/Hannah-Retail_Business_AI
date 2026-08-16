import * as THREE from
    "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";


/* =========================================================
   CONTAINER
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
        0xff7a00;

    const BRIGHT_ORANGE =
        0xffa33a;

    const WHITE =
        0xffffff;


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


    camera.position.z =
        4;


    /* =====================================================
       RENDERER
       ===================================================== */

    const renderer =
        new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
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


        /*
         * The voice overlay may initially
         * be hidden.
         *
         * Do not try to render a 0x0 canvas.
         */

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


    /*
     * ResizeObserver is important because
     * the voice overlay can change from
     * hidden -> visible without a window resize.
     */

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
       OUTER WAVE SPHERE
       ===================================================== */

    const geometry =
        new THREE.SphereGeometry(
            1,
            64,
            64
        );


    const material =
        new THREE.MeshBasicMaterial({

            color:
                ORANGE,

            wireframe:
                true,

            transparent:
                true,

            opacity:
                0.30

        });


    const orb =
        new THREE.Mesh(
            geometry,
            material
        );


    scene.add(
        orb
    );


    /* =====================================================
       SECOND WAVE LAYER
       ===================================================== */

    const waveGeometry =
        new THREE.SphereGeometry(
            1.08,
            48,
            48
        );


    const waveMaterial =
        new THREE.MeshBasicMaterial({

            color:
                BRIGHT_ORANGE,

            wireframe:
                true,

            transparent:
                true,

            opacity:
                0.12

        });


    const wave =
        new THREE.Mesh(
            waveGeometry,
            waveMaterial
        );


    scene.add(
        wave
    );


    /* =====================================================
       INNER CORE
       ===================================================== */

    const coreGeometry =
        new THREE.SphereGeometry(
            0.38,
            48,
            48
        );


    const coreMaterial =
        new THREE.MeshBasicMaterial({

            color:
                WHITE,

            transparent:
                true,

            opacity:
                0.88

        });


    const core =
        new THREE.Mesh(
            coreGeometry,
            coreMaterial
        );


    scene.add(
        core
    );


    /* =====================================================
       INNER ORANGE CORE
       ===================================================== */

    const innerCoreGeometry =
        new THREE.SphereGeometry(
            0.22,
            32,
            32
        );


    const innerCoreMaterial =
        new THREE.MeshBasicMaterial({

            color:
                BRIGHT_ORANGE,

            transparent:
                true,

            opacity:
                0.65

        });


    const innerCore =
        new THREE.Mesh(
            innerCoreGeometry,
            innerCoreMaterial
        );


    scene.add(
        innerCore
    );


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
            "Orb audio system initialized."
        );

    }


    /* =====================================================
       CONNECT AUDIO
       ===================================================== */

    function connectAudio(
        audio
    ) {

        initializeAudio();


        if (
            audioContext.state ===
            "suspended"
        ) {

            audioContext.resume();

        }


        /*
         * Every HTMLAudioElement created
         * by script.js is new, so creating
         * its MediaElementSource once is safe.
         */

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
                "Orb connected to audio."
            );

        } catch (error) {

            console.error(
                "Orb audio connection failed:",
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


        /*
         * Give lower frequencies
         * slightly more importance.
         */

        const length =
            audioData.length;


        for (
            let i = 0;
            i < length;
            i++
        ) {

            const weight =
                i < length * 0.35
                    ? 1.4
                    : 0.8;


            total +=
                audioData[i] *
                weight;

        }


        const average =
            total /
            length;


        targetAudioLevel =
            Math.min(
                average / 180,
                1
            );


        /*
         * Smooth the movement.
         */

        audioLevel +=
            (
                targetAudioLevel -
                audioLevel
            ) * 0.28;

    }


    /* =====================================================
       ANIMATION
       ===================================================== */

    let time =
        0;


    function animate() {

        requestAnimationFrame(
            animate
        );


        time +=
            0.01;


        updateAudioLevel();


        /* =================================================
           IDLE MOVEMENT
           ================================================= */

        orb.rotation.x +=
            0.0015;


        orb.rotation.y +=
            0.0025;


        wave.rotation.x -=
            0.001;


        wave.rotation.y +=
            0.0015;


        /* =================================================
           AUDIO VIBRATION
           ================================================= */

        const vibration =
            audioLevel;


        /*
         * Main sphere expands.
         */

        const orbScale =
            1 +
            vibration * 0.55;


        orb.scale.set(
            orbScale,
            orbScale,
            orbScale
        );


        /*
         * Second wave expands
         * more aggressively.
         */

        const wavePulse =
            1.04 +
            vibration * 0.9;


        wave.scale.set(
            wavePulse,
            wavePulse,
            wavePulse
        );


        /*
         * Core reacts strongly.
         */

        const coreScale =
            1 +
            vibration * 1.7;


        core.scale.set(
            coreScale,
            coreScale,
            coreScale
        );


        const innerScale =
            1 +
            vibration * 2.4;


        innerCore.scale.set(
            innerScale,
            innerScale,
            innerScale
        );


        /* =================================================
           SMALL FLOATING VIBRATION
           ================================================= */

        orb.position.y =
            Math.sin(
                time * 2
            ) *
            0.015;


        wave.position.y =
            Math.sin(
                time * 2.5
            ) *
            0.025;


        core.position.y =
            Math.sin(
                time * 3
            ) *
            0.008;


        /* =================================================
           OPACITY
           ================================================= */

        material.opacity =
            0.28 +
            vibration * 0.58;


        waveMaterial.opacity =
            0.08 +
            vibration * 0.32;


        coreMaterial.opacity =
            0.75 +
            vibration * 0.25;


        innerCoreMaterial.opacity =
            0.35 +
            vibration * 0.55;


        /* =================================================
           RENDER
           ================================================= */

        renderer.render(
            scene,
            camera
        );

    }


    animate();


    /* =====================================================
       GLOBAL FUNCTIONS
       ===================================================== */

    window.initializeOrbAudio =
        initializeAudio;


    window.connectOrbToAudio =
        connectAudio;


    /*
     * Useful for debugging.
     */

    window.resizeHannahOrb =
        resizeRenderer;

}