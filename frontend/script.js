const micButton = document.getElementById("micButton");
const statusText = document.getElementById("status");

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;

let recognition = null;

let isListening = false;
let isProcessing = false;
let isSpeaking = false;

let speechQueue = [];
let speechWorkerRunning = false;
let currentAudio = null;

let currentChatController = null;
let requestId = 0;


/*
 * TTS settings
 *
 * Short responses are spoken as one complete response.
 * Longer responses are split into larger natural chunks.
 */

const SHORT_RESPONSE_LIMIT = 250;
const TTS_BATCH_SIZE = 1000;


/* =========================================================
   SPEECH RECOGNITION
   ========================================================= */

if (!SpeechRecognition) {

    statusText.textContent =
        "BROWSER NOT SUPPORTED";

} else {

    recognition = new SpeechRecognition();

    recognition.lang = "en-US";

    recognition.continuous = false;

    recognition.interimResults = false;


    micButton.addEventListener(
        "click",
        handleMicClick
    );


    /*
     * Recognition started.
     */

    recognition.onstart = () => {

        console.log(
            "VOICE DEBUG: recognition started"
        );

        isListening = true;

        updateStatus(
            "LISTENING"
        );

    };


    /*
     * Speech result received.
     */

    recognition.onresult = async (event) => {

        console.log(
            "VOICE DEBUG: result received",
            event
        );


        if (!isListening) {

            console.log(
                "VOICE DEBUG: ignoring result because not listening"
            );

            return;

        }


        const text =
            event.results[0][0]
                .transcript
                .trim();


        console.log(
            "User said:",
            text
        );


        if (!text) {

            console.log(
                "VOICE DEBUG: empty speech result"
            );

            return;

        }


        isListening = false;

        isProcessing = true;


        updateStatus(
            "PROCESSING"
        );


        try {

            await processQuestion(
                text
            );

        } catch (error) {

            if (
                error.name ===
                "AbortError"
            ) {

                console.log(
                    "Previous request cancelled."
                );

                return;

            }


            console.error(
                "RetailAI error:",
                error
            );


            updateStatus(
                "ERROR"
            );

        } finally {

            isProcessing = false;

        }

    };


    /*
     * Recognition error.
     */

    recognition.onerror = (event) => {

        console.error(
            "VOICE DEBUG: recognition error:",
            event.error
        );


        isListening = false;


        /*
         * Aborted is normally caused by
         * intentionally stopping recognition.
         */

        if (
            event.error ===
            "aborted"
        ) {

            return;

        }


        updateStatus(
            "READY"
        );

    };


    /*
     * Recognition ended.
     */

    recognition.onend = () => {

        console.log(
            "VOICE DEBUG: recognition ended",
            {
                isListening: isListening,
                isProcessing: isProcessing,
                isSpeaking: isSpeaking
            }
        );


        isListening = false;


        /*
         * Do not change READY while
         * processing or speaking.
         */

        if (
            !isProcessing &&
            !isSpeaking
        ) {

            updateStatus(
                "READY"
            );

        }

    };

}


/* =========================================================
   MICROPHONE BUTTON
   ========================================================= */

function handleMicClick() {

    console.log(
        "MIC CLICK",
        {
            isListening: isListening,
            isProcessing: isProcessing,
            isSpeaking: isSpeaking
        }
    );


    /*
     * If already listening,
     * stop the microphone.
     */

    if (isListening) {

        stopListening();

        return;

    }


    /*
     * Don't start another request while
     * Hannah is processing or speaking.
     */

    if (
        isProcessing ||
        isSpeaking
    ) {

        console.log(
            "Hannah is busy."
        );

        return;

    }


    startListening();

}


/* =========================================================
   START LISTENING
   ========================================================= */

function startListening() {

    if (!recognition) {

        return;

    }


    if (isListening) {

        return;

    }


    try {

        updateStatus(
            "LISTENING"
        );


        console.log(
            "VOICE DEBUG: calling recognition.start()"
        );


        recognition.start();

    } catch (error) {

        console.error(
            "Could not start recognition:",
            error
        );


        isListening = false;


        updateStatus(
            "READY"
        );

    }

}

/* =========================================================
   STOP LISTENING
   ========================================================= */

function stopListening() {

    if (!recognition) {

        return;

    }


    console.log(
        "VOICE DEBUG: stopping recognition"
    );


    isListening = false;


    try {

        recognition.stop();

    } catch (error) {

        console.error(
            "Could not stop recognition:",
            error
        );

    }


    /*
     * Don't force READY if something
     * else is already processing.
     */

    if (
        !isProcessing &&
        !isSpeaking
    ) {

        updateStatus(
            "READY"
        );

    }

}


/* =========================================================
   CANCEL PREVIOUS REQUEST
   ========================================================= */

function cancelPreviousRequest() {

    /*
     * Cancel previous chat request.
     */

    if (
        currentChatController
    ) {

        console.log(
            "Cancelling previous chat request."
        );


        currentChatController.abort();

        currentChatController = null;

    }


    /*
     * Stop currently playing audio.
     */

    if (currentAudio) {

        try {

            currentAudio.pause();

            currentAudio.currentTime = 0;

        } catch (error) {

            console.error(
                "Could not stop audio:",
                error
            );

        }


        currentAudio = null;

    }


    /*
     * Remove queued speech from
     * the previous request.
     */

    speechQueue = [];

    speechWorkerRunning = false;

    isSpeaking = false;

}


/* =========================================================
   PROCESS QUESTION
   ========================================================= */

async function processQuestion(text) {

    /*
     * Give every request its own ID.
     */

    const thisRequestId =
        ++requestId;


    /*
     * Cancel anything left over
     * from the previous request.
     */

    cancelPreviousRequest();


    /*
     * Create a new controller.
     */

    currentChatController =
        new AbortController();


    console.log(
        "CHAT DEBUG: sending question",
        text
    );


    const response =
        await fetch(
            "/chat/stream",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    question: text
                }),

                signal:
                    currentChatController
                        .signal,

                cache: "no-store"
            }
        );


    if (!response.ok) {

        throw new Error(
            `Chat stream failed: ${response.status}`
        );

    }


    if (!response.body) {

        throw new Error(
            "Streaming is not supported by this browser."
        );

    }


    const reader =
        response.body.getReader();


    const decoder =
        new TextDecoder();


    let buffer = "";

    let completeResponse = "";

    let speechBuffer = "";


    /* =====================================================
       READ STREAM
       ===================================================== */

    while (true) {

        const {
            value,
            done
        } = await reader.read();


        if (done) {

            break;

        }


        /*
         * Ignore data belonging to
         * an older request.
         */

        if (
            thisRequestId !==
            requestId
        ) {

            console.log(
                "CHAT DEBUG: ignoring old request"
            );

            return;

        }


        buffer +=
            decoder.decode(
                value,
                {
                    stream: true
                }
            );


        const lines =
            buffer.split("\n");


        buffer =
            lines.pop();


        for (
            const line of lines
        ) {

            if (!line.trim()) {

                continue;

            }


            let event;


            try {

                event =
                    JSON.parse(line);

            } catch (error) {

                console.error(
                    "Invalid stream event:",
                    line
                );

                continue;

            }


            console.log(
                "Stream event:",
                event
            );


            /*
             * Ignore events from
             * older requests.
             */

            if (
                thisRequestId !==
                requestId
            ) {

                return;

            }


            /* =================================================
               STATUS EVENT
               ================================================= */

            if (
                event.type ===
                "status"
            ) {

                updateStatus(
                    event.status
                );

            }


            /* =================================================
               TEXT EVENT
               ================================================= */

            if (
                event.type ===
                "text"
            ) {

                const content =
                    event.content || "";


                completeResponse +=
                    content;


                speechBuffer +=
                    content;


                /*
                 * Don't send tiny pieces of
                 * a short answer to TTS.
                 */

                if (
                    completeResponse.length <
                    SHORT_RESPONSE_LIMIT
                ) {

                    continue;

                }


                /*
                 * Long response:
                 * create larger TTS batches.
                 */

                const batch =
                    getSpeechBatch(
                        speechBuffer
                    );


                if (
                    batch.text
                ) {

                    enqueueSpeech(
                        batch.text
                    );


                    speechBuffer =
                        batch.remaining;

                }

            }


            /* =================================================
               ERROR EVENT
               ================================================= */

            if (
                event.type ===
                "error"
            ) {

                throw new Error(
                    event.content
                );

            }


            /* =================================================
               DONE EVENT
               ================================================= */

            if (
                event.type ===
                "done"
            ) {

                console.log(
                    "Streaming complete."
                );

            }

        }

    }


    /*
     * Process a final partial line.
     */

    if (
        buffer.trim()
    ) {

        try {

            const event =
                JSON.parse(buffer);


            if (
                event.type ===
                "text"
            ) {

                const content =
                    event.content || "";


                completeResponse +=
                    content;


                speechBuffer +=
                    content;

            }

        } catch (error) {

            console.error(
                "Could not process final stream data:",
                buffer
            );

        }

    }


    /*
     * ========================================================
     * FINAL TTS HANDLING
     * ========================================================
     *
     * Short response:
     * one complete TTS request.
     *
     * Long response:
     * send remaining accumulated text.
     */

    if (
        completeResponse.trim()
    ) {

        if (
            completeResponse.length <
            SHORT_RESPONSE_LIMIT
        ) {

            enqueueSpeech(
                completeResponse
            );

        } else {

            if (
                speechBuffer.trim()
            ) {

                enqueueSpeech(
                    speechBuffer
                );

            }

        }

    }


    currentChatController =
        null;


    /*
     * If there is no voice work,
     * return to READY.
     */

    if (
        speechQueue.length === 0 &&
        !speechWorkerRunning &&
        !isSpeaking
    ) {

        updateStatus(
            "READY"
        );

    }

}


/* =========================================================
   TTS BATCHING
   ========================================================= */

function getSpeechBatch(text) {

    if (
        text.length <
        TTS_BATCH_SIZE
    ) {

        return {
            text: "",
            remaining: text
        };

    }


    /*
     * Prefer a sentence boundary.
     */

    const sentenceEnd =
        findSentenceBoundary(
            text,
            TTS_BATCH_SIZE
        );


    if (
        sentenceEnd > 0
    ) {

        return {

            text:
                text
                    .slice(
                        0,
                        sentenceEnd
                    )
                    .trim(),

            remaining:
                text
                    .slice(
                        sentenceEnd
                    )
                    .trim()

        };

    }


    /*
     * If no sentence boundary exists,
     * cut at the nearest space.
     */

    const spaceIndex =
        text.lastIndexOf(
            " ",
            TTS_BATCH_SIZE
        );


    if (
        spaceIndex > 0
    ) {

        return {

            text:
                text
                    .slice(
                        0,
                        spaceIndex
                    )
                    .trim(),

            remaining:
                text
                    .slice(
                        spaceIndex
                    )
                    .trim()

        };

    }


    return {
        text: "",
        remaining: text
    };

}


/* =========================================================
   FIND SENTENCE BOUNDARY
   ========================================================= */

function findSentenceBoundary(
    text,
    minimumPosition
) {

    const part =
        text.slice(
            0,
            minimumPosition
        );


    const matches =
        [
            ...part.matchAll(
                /[.!?](?:\s|$)/g
            )
        ];


    if (
        matches.length === 0
    ) {

        return -1;

    }


    const lastMatch =
        matches[
            matches.length - 1
        ];


    return (
        lastMatch.index + 1
    );

}


/* =========================================================
   TTS QUEUE
   ========================================================= */

function enqueueSpeech(text) {

    const cleanedText =
        cleanTextForSpeech(
            text
        );


    if (!cleanedText) {

        return;

    }


    console.log(
        "TTS DEBUG: queueing",
        cleanedText
    );


    speechQueue.push(
        cleanedText
    );


    runSpeechWorker();

}


/* =========================================================
   TTS WORKER
   ========================================================= */

async function runSpeechWorker() {

    if (
        speechWorkerRunning
    ) {

        return;

    }


    speechWorkerRunning =
        true;


    while (
        speechQueue.length > 0
    ) {

        const text =
            speechQueue.shift();


        try {

            await speakResponse(
                text
            );

        } catch (error) {

            console.error(
                "Speech error:",
                error
            );


            updateStatus(
                "VOICE ERROR"
            );


            break;

        }

    }


    speechWorkerRunning =
        false;


    isSpeaking = false;


    /*
     * READY only after the complete
     * audio queue has finished.
     */

    if (
        !isListening &&
        !isProcessing
    ) {

        updateStatus(
            "READY"
        );

    }

}


/* =========================================================
   TEXT TO SPEECH
   ========================================================= */

async function speakResponse(text) {

    updateStatus(
        "PREPARING VOICE"
    );


    console.log(
        "TTS DEBUG: sending",
        text
    );


    const response =
        await fetch(
            "/voice/speak",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    text: text
                }),

                cache: "no-store"
            }
        );


    if (!response.ok) {

        throw new Error(
            `TTS request failed: ${response.status}`
        );

    }


    const audioBlob =
        await response.blob();


    const audioUrl =
        URL.createObjectURL(
            audioBlob
        );


    const audio =
        new Audio(audioUrl);


    currentAudio =
        audio;


    /*
     * Connect audio to the visualizer.
     */

    if (
        window.connectOrbToAudio
    ) {

        window.connectOrbToAudio(
            audio
        );

    }


    /*
     * Wait for actual playback
     * to finish before continuing.
     */

    await new Promise(
        (resolve, reject) => {

            audio.onplay = () => {

                isSpeaking =
                    true;


                updateStatus(
                    "SPEAKING"
                );


                console.log(
                    "VOICE DEBUG: audio started"
                );

            };


            audio.onended = () => {

                isSpeaking =
                    false;


                console.log(
                    "VOICE DEBUG: audio ended"
                );


                if (
                    currentAudio ===
                    audio
                ) {

                    currentAudio =
                        null;

                }


                URL.revokeObjectURL(
                    audioUrl
                );


                resolve();

            };


            audio.onerror = () => {

                isSpeaking =
                    false;


                if (
                    currentAudio ===
                    audio
                ) {

                    currentAudio =
                        null;

                }


                URL.revokeObjectURL(
                    audioUrl
                );


                reject(
                    new Error(
                        "Audio playback failed."
                    )
                );

            };


            audio.play()
                .catch(
                    reject
                );

        }
    );

}


/* =========================================================
   CLEAN TEXT FOR SPEECH
   ========================================================= */

function cleanTextForSpeech(text) {

    return text

        /*
         * Remove bold.
         */

        .replace(
            /\*\*/g,
            ""
        )

        /*
         * Remove italic.
         */

        .replace(
            /\*/g,
            ""
        )

        /*
         * Remove inline code.
         */

        .replace(
            /`/g,
            ""
        )

        /*
         * Remove headings.
         */

        .replace(
            /^#+\s*/gm,
            ""
        )

        /*
         * Convert markdown links
         * to visible text.
         */

        .replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        )

        /*
         * Remove bullet markers.
         */

        .replace(
            /^\s*[-•]\s*/gm,
            ""
        )

        /*
         * Remove excessive whitespace.
         */

        .replace(
            /\s+/g,
            " "
        )

        .trim();

}


/* =========================================================
   STATUS
   ========================================================= */

function updateStatus(status) {

    const displayStatus =
        status.toUpperCase();


    /*
     * Restart status animation.
     */

    statusText.classList.remove(
        "status-change"
    );


    void statusText.offsetWidth;


    statusText.textContent =
        displayStatus;


    statusText.classList.add(
        "status-change"
    );

}

