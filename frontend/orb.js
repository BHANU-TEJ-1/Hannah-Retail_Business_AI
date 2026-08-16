import * as THREE from
    "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";


const orbContainer =
    document.getElementById("orb-container");


let audioContext = null;

let analyser = null;

let audioData = null;

let audioLevel = 0;

let targetAudioLevel = 0;


if (!orbContainer) {

    console.error(
        "orb-container was not found."
    );

} else {

    // =========================
    // SCENE
    // =========================

    const scene =
        new THREE.Scene();


    // =========================
    // CAMERA
    // =========================

    const camera =
        new THREE.PerspectiveCamera(
            45,
            orbContainer.clientWidth /
                orbContainer.clientHeight,
            0.1,
            100
        );


    camera.position.z = 4;


    // =========================
    // RENDERER
    // =========================

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


    renderer.setSize(
        orbContainer.clientWidth,
        orbContainer.clientHeight
    );


    orbContainer.appendChild(
        renderer.domElement
    );


    // =========================
    // OUTER SPHERE
    // =========================

    const geometry =
        new THREE.SphereGeometry(
            1,
            64,
            64
        );


    const material =
        new THREE.MeshBasicMaterial({

            color: 0x00eaff,

            wireframe: true,

            transparent: true,

            opacity: 0.45

        });


    const orb =
        new THREE.Mesh(
            geometry,
            material
        );


    scene.add(orb);


    // =========================
    // INNER CORE
    // =========================

    const coreGeometry =
        new THREE.SphereGeometry(
            0.42,
            48,
            48
        );


    const coreMaterial =
        new THREE.MeshBasicMaterial({

            color: 0xffffff,

            transparent: true,

            opacity: 0.9

        });


    const core =
        new THREE.Mesh(
            coreGeometry,
            coreMaterial
        );


    scene.add(core);


    // =========================
    // AUDIO INITIALIZATION
    // =========================

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
            256;


        analyser.smoothingTimeConstant =
            0.75;


        audioData =
            new Uint8Array(
                analyser.frequencyBinCount
            );


        console.log(
            "Orb audio system initialized."
        );

    }


    // =========================
    // CONNECT AUDIO
    // =========================

    function connectAudio(audio) {

        initializeAudio();


        if (
            audioContext.state ===
            "suspended"
        ) {

            audioContext.resume();

        }


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

    }


    // =========================
    // AUDIO ANALYSIS
    // =========================

    function updateAudioLevel() {

        if (
            !analyser ||
            !audioData
        ) {

            targetAudioLevel = 0;

            return;

        }


        analyser.getByteFrequencyData(
            audioData
        );


        let total = 0;


        for (
            let i = 0;
            i < audioData.length;
            i++
        ) {

            total +=
                audioData[i];

        }


        const average =
            total /
            audioData.length;


        targetAudioLevel =
            average / 255;


        /*
         * Make the movement much
         * more visible.
         */

        audioLevel +=
            (
                targetAudioLevel -
                audioLevel
            ) * 0.35;

    }


    // =========================
    // ANIMATION
    // =========================

    function animate() {

        requestAnimationFrame(
            animate
        );


        updateAudioLevel();


        /*
         * Idle movement.
         */

        orb.rotation.x +=
            0.002;


        orb.rotation.y +=
            0.004;


        /*
         * Audio movement.
         */

        const audioScale =
            audioLevel * 0.8;


        const orbScale =
            1 +
            audioScale;


        orb.scale.set(
            orbScale,
            orbScale,
            orbScale
        );


        /*
         * Core reacts more strongly.
         */

        const coreScale =
            1 +
            audioLevel * 1.5;


        core.scale.set(
            coreScale,
            coreScale,
            coreScale
        );


        /*
         * Make the glow stronger
         * while speaking.
         */

        material.opacity =
            0.35 +
            audioLevel * 0.6;


        coreMaterial.opacity =
            0.75 +
            audioLevel * 0.25;


        renderer.render(
            scene,
            camera
        );

    }


    animate();


    // =========================
    // RESIZE
    // =========================

    window.addEventListener(
        "resize",
        () => {

            const width =
                orbContainer.clientWidth;

            const height =
                orbContainer.clientHeight;


            camera.aspect =
                width / height;


            camera.updateProjectionMatrix();


            renderer.setSize(
                width,
                height
            );

        }
    );


    // =========================
    // GLOBAL FUNCTIONS
    // =========================

    window.initializeOrbAudio =
        initializeAudio;


    window.connectOrbToAudio =
        connectAudio;

}