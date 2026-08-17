/* =========================================================
   RETAILAI / HANNAH
   Chat + Voice Interface
   ========================================================= */


/* =========================================================
   DOM
   ========================================================= */

const micButton =
    document.getElementById("micButton");

const statusText =
    document.getElementById("status");

const messageInput =
    document.getElementById("messageInput");

const sendButton =
    document.getElementById("sendButton");

const messages =
    document.getElementById("messages");

const chatArea =
    document.getElementById("chatArea");

const welcome =
    document.getElementById("welcome");

const voiceMode =
    document.getElementById("voiceMode");

const voiceCore =
    document.querySelector(".voice-core");


/* =========================================================
   SPEECH RECOGNITION
   ========================================================= */

const SpeechRecognition =
    window.SpeechRecognition ||
    window.webkitSpeechRecognition;


let recognition = null;


/* =========================================================
   STATE
   ========================================================= */

let isListening = false;

let isProcessing = false;

let isSpeaking = false;

let speechQueue = [];

let speechWorkerRunning = false;

let currentAudio = null;

let currentRequestId = 0;

let currentChatController = null;

let currentRequestIsVoice = false;


/* =========================================================
   INITIALIZATION
   ========================================================= */

if (!SpeechRecognition) {

    console.warn(
        "Speech recognition is not supported."
    );

} else {

    recognition =
        new SpeechRecognition();

    recognition.lang =
        "en-US";

    recognition.continuous =
        false;

    recognition.interimResults =
        false;

    recognition.onstart =
        handleRecognitionStart;

    recognition.onresult =
        handleRecognitionResult;

    recognition.onerror =
        handleRecognitionError;

    recognition.onend =
        handleRecognitionEnd;
}


/* =========================================================
   BUTTON EVENTS
   ========================================================= */

if (sendButton) {

    sendButton.addEventListener(
        "click",
        sendTextMessage
    );

}


if (messageInput) {

    messageInput.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Enter" &&
                !event.shiftKey
            ) {

                event.preventDefault();

                sendTextMessage();

            }

        }
    );


    messageInput.addEventListener(
        "input",
        resizeInput
    );

}


if (micButton) {

    micButton.addEventListener(
        "click",
        handleMicButton
    );

}


if (voiceCore) {

    voiceCore.addEventListener(
        "click",
        handleVoiceCoreClick
    );

}


/* =========================================================
   TEXT CHAT
   ========================================================= */

async function sendTextMessage() {

    if (!messageInput) {
        return;
    }


    if (
        isProcessing ||
        isSpeaking ||
        isListening
    ) {

        return;

    }


    const text =
        messageInput.value.trim();


    if (!text) {
        return;
    }


    isProcessing =
        true;


    messageInput.value =
        "";


    resizeInput();


    appendMessage(
        "user",
        text
    );


    try {

        await processQuestion(
            text,
            false
        );

    } catch (error) {

        console.error(
            "TEXT CHAT ERROR:",
            error
        );


        appendMessage(
            "assistant",
            "Sorry sir, I could not complete that request."
        );

    } finally {

        isProcessing =
            false;

    }

}


/* =========================================================
   VOICE BUTTON
   ========================================================= */

function handleMicButton() {

    console.log(
        "MIC BUTTON",
        {
            isListening,
            isProcessing,
            isSpeaking
        }
    );


    if (!recognition) {
        return;
    }


    if (isListening) {

        stopListening();

        return;

    }


    if (
        isProcessing ||
        isSpeaking
    ) {

        return;

    }


    openVoiceMode();

    startListening();

}


/* =========================================================
   VOICE CORE
   ========================================================= */

function handleVoiceCoreClick() {

    if (!recognition) {
        return;
    }


    if (isListening) {

        stopListening();

        return;

    }


    if (
        isProcessing ||
        isSpeaking
    ) {

        return;

    }


    startListening();

}


/* =========================================================
   OPEN VOICE MODE
   ========================================================= */

function openVoiceMode() {

    if (!voiceMode) {
        return;
    }


    voiceMode.classList.add(
        "active"
    );


    voiceMode.setAttribute(
        "aria-hidden",
        "false"
    );


    if (
        window.resizeHannahOrb
    ) {

        requestAnimationFrame(
            () => {

                window.resizeHannahOrb();

            }
        );

    }

}


/* =========================================================
   CLOSE VOICE MODE
   ========================================================= */

function closeVoiceMode() {

    if (!voiceMode) {
        return;
    }


    voiceMode.classList.remove(
        "active"
    );


    voiceMode.setAttribute(
        "aria-hidden",
        "true"
    );

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


    if (
        isProcessing ||
        isSpeaking
    ) {

        return;

    }


    try {

        updateStatus(
            "LISTENING"
        );


        recognition.start();

    } catch (error) {

        console.error(
            "Could not start recognition:",
            error
        );


        isListening =
            false;


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


    isListening =
        false;


    try {

        recognition.stop();

    } catch (error) {

        console.error(
            "Could not stop recognition:",
            error
        );

    }


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
   RECOGNITION START
   ========================================================= */

function handleRecognitionStart() {

    isListening =
        true;


    updateStatus(
        "LISTENING"
    );

}


/* =========================================================
   RECOGNITION RESULT
   ========================================================= */

async function handleRecognitionResult(
    event
) {

    const text =
        event.results[0][0]
            .transcript
            .trim();


    if (!text) {
        return;
    }


    isListening =
        false;


    isProcessing =
        true;


    appendMessage(
        "user",
        text
    );


    updateStatus(
        "PROCESSING"
    );


    try {

        await processQuestion(
            text,
            true
        );

    } catch (error) {

        console.error(
            "RetailAI voice error:",
            error
        );


        updateStatus(
            "ERROR"
        );

    } finally {

        isProcessing =
            false;

    }

}


/* =========================================================
   RECOGNITION ERROR
   ========================================================= */

function handleRecognitionError(
    event
) {

    console.error(
        "VOICE DEBUG: recognition error:",
        event.error
    );


    isListening =
        false;


    if (
        event.error === "aborted"
    ) {

        return;

    }


    updateStatus(
        "READY"
    );

}


/* =========================================================
   RECOGNITION END
   ========================================================= */

function handleRecognitionEnd() {

    isListening =
        false;


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
   MAIN QUESTION PROCESSOR
   ========================================================= */

async function processQuestion(
    text,
    isVoiceRequest = false
) {

    const thisRequestId =
        ++currentRequestId;


    currentRequestIsVoice =
        isVoiceRequest;


    cancelPreviousRequest();


    currentChatController =
        new AbortController();


    let assistantMessage =
        null;


    if (!isVoiceRequest) {

        assistantMessage =
            createAssistantMessage();

    }


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

                cache:
                    "no-store"

            }
        );


    if (!response.ok) {

        throw new Error(
            `Chat stream failed: ${response.status}`
        );

    }


    if (!response.body) {

        throw new Error(
            "Streaming is not supported."
        );

    }


    const reader =
        response.body.getReader();


    const decoder =
        new TextDecoder();


    let buffer = "";

    let speechBuffer = "";


    while (true) {

        const {
            value,
            done
        } = await reader.read();


        if (done) {
            break;
        }


        if (
            thisRequestId !==
            currentRequestId
        ) {

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


            if (
                thisRequestId !==
                currentRequestId
            ) {

                return;

            }


            /* =================================================
               STATUS
               ================================================= */

            if (
                event.type ===
                "status"
            ) {

                if (isVoiceRequest) {

                    updateStatus(
                        event.status
                    );

                }

            }


            /* =================================================
               TEXT
               ================================================= */

            if (
                event.type ===
                "text"
            ) {

                const content =
                    event.content || "";


                if (
                    assistantMessage
                ) {

                    appendAssistantText(
                        assistantMessage,
                        content
                    );

                }


                if (isVoiceRequest) {

                    speechBuffer +=
                        content;

                }

            }


            /* =================================================
               ERROR
               ================================================= */

            if (
                event.type ===
                "error"
            ) {

                throw new Error(
                    event.content
                );

            }

        }

    }


    /* =====================================================
       FINAL PARTIAL LINE
       ===================================================== */

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


                if (
                    assistantMessage
                ) {

                    appendAssistantText(
                        assistantMessage,
                        content
                    );

                }


                if (
                    isVoiceRequest
                ) {

                    speechBuffer +=
                        content;

                }

            }

        } catch (error) {

            console.error(
                "Could not process final stream data:",
                buffer
            );

        }

    }


    currentChatController =
        null;


    /* =====================================================
       VOICE TTS
       ===================================================== */

    if (
        isVoiceRequest &&
        speechBuffer.trim()
    ) {

        enqueueSpeech(
            speechBuffer
        );

    }


    /* =====================================================
       TEXT MODE
       ===================================================== */

    if (
        !isVoiceRequest
    ) {

        isProcessing =
            false;

        return;

    }


    /* =====================================================
       VOICE FINISHED
       ===================================================== */

    if (
        speechQueue.length === 0 &&
        !speechWorkerRunning &&
        !isSpeaking
    ) {

        updateStatus(
            "READY"
        );


        closeVoiceMode();

    }

}


/* =========================================================
   CANCEL PREVIOUS REQUEST
   ========================================================= */

function cancelPreviousRequest() {

    if (
        currentChatController
    ) {

        try {

            currentChatController.abort();

        } catch (error) {

            console.error(
                "Could not cancel request:",
                error
            );

        }


        currentChatController =
            null;

    }


    if (currentAudio) {

        try {

            currentAudio.pause();

            currentAudio.currentTime =
                0;

        } catch (error) {

            console.error(
                "Could not stop audio:",
                error
            );

        }


        currentAudio =
            null;

    }


    speechQueue =
        [];


    speechWorkerRunning =
        false;


    isSpeaking =
        false;

}


/* =========================================================
   CREATE MESSAGE
   ========================================================= */

function appendMessage(
    role,
    text
) {

    if (!messages) {
        return;
    }


    if (welcome) {

        welcome.style.display =
            "none";

    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${role}`;


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    content.textContent =
        text;


    message.appendChild(
        content
    );


    messages.appendChild(
        message
    );


    scrollChatToBottom();


    return message;

}


/* =========================================================
   CREATE ASSISTANT MESSAGE
   ========================================================= */

function createAssistantMessage() {

    if (!messages) {
        return null;
    }


    if (welcome) {

        welcome.style.display =
            "none";

    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        "message assistant";


    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "assistant-wrapper";


    const label =
        document.createElement(
            "div"
        );


    label.className =
        "message-label";


    label.textContent =
        "HANNAH";


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    wrapper.appendChild(
        label
    );


    wrapper.appendChild(
        content
    );


    message.appendChild(
        wrapper
    );


    messages.appendChild(
        message
    );


    scrollChatToBottom();


    return content;

}


/* =========================================================
   STREAM ASSISTANT TEXT
   ========================================================= */

function appendAssistantText(
    element,
    text
) {

    if (!element) {
        return;
    }


    element.textContent +=
        text;


    scrollChatToBottom();

}


/* =========================================================
   CHAT SCROLL
   ========================================================= */

function scrollChatToBottom() {

    if (!chatArea) {
        return;
    }


    requestAnimationFrame(
        () => {

            chatArea.scrollTop =
                chatArea.scrollHeight;

        }
    );

}


/* =========================================================
   TEXTAREA RESIZE
   ========================================================= */

function resizeInput() {

    if (!messageInput) {
        return;
    }


    messageInput.style.height =
        "auto";


    messageInput.style.height =
        `${Math.min(
            messageInput.scrollHeight,
            140
        )}px`;

}


/* =========================================================
   TTS QUEUE
   ========================================================= */

function enqueueSpeech(
    text
) {

    const cleanedText =
        cleanTextForSpeech(
            text
        );


    if (!cleanedText) {
        return;
    }


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


    isSpeaking =
        false;


    if (
        currentRequestIsVoice
    ) {

        updateStatus(
            "READY"
        );


        closeVoiceMode();

    }

}


/* =========================================================
   TTS
   ========================================================= */

async function speakResponse(
    text
) {

    updateStatus(
        "PREPARING VOICE"
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

                cache:
                    "no-store"

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
        new Audio(
            audioUrl
        );


    currentAudio =
        audio;


    /*
     * Connect the actual Hannah
     * voice audio to the orb.
     */

    if (
        window.connectOrbToAudio
    ) {

        window.connectOrbToAudio(
            audio
        );

    }


    await new Promise(
        (resolve, reject) => {

            audio.onplay =
                () => {

                    isSpeaking =
                        true;


                    updateStatus(
                        "SPEAKING"
                    );

                };


            audio.onended =
                () => {

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


                    resolve();

                };


            audio.onerror =
                () => {

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
   CLEAN TTS TEXT
   ========================================================= */

function cleanTextForSpeech(
    text
) {

    return text

        .replace(
            /\*\*/g,
            ""
        )

        .replace(
            /\*/g,
            ""
        )

        .replace(
            /`/g,
            ""
        )

        .replace(
            /^#+\s*/gm,
            ""
        )

        .replace(
            /\[([^\]]+)\]\([^)]+\)/g,
            "$1"
        )

        .replace(
            /^\s*[-•]\s*/gm,
            ""
        )

        .replace(
            /[\u{1F300}-\u{1FAFF}]/gu,
            ""
        )

        .replace(
            /\s+/g,
            " "
        )

        .trim();

}


/* =========================================================
   STATUS
   ========================================================= */

function updateStatus(
    status
) {

    if (!statusText) {
        return;
    }


    const displayStatus =
        String(
            status || "READY"
        ).toUpperCase();


    statusText.classList.remove(
        "status-change"
    );


    void statusText.offsetWidth;


    statusText.textContent =
        displayStatus;


    statusText.classList.add(
        "status-change"
    );


    /*
     * Directly tell the orb what
     * Hannah is doing.
     */

    if (
        window.setHannahOrbState
    ) {

        window.setHannahOrbState(
            displayStatus
        );

    }

}