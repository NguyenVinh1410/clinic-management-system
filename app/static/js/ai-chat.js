let aiChatSessionId = null;
let aiChatInitialized = false;


document.addEventListener(
    "DOMContentLoaded",
    () => {

        setupAIChat();

    }
);


function setupAIChat() {

    const toggle =
        document.getElementById(
            "aiChatToggle"
        );

    const close =
        document.getElementById(
            "aiChatClose"
        );

    const box =
        document.getElementById(
            "aiChatBox"
        );

    const form =
        document.getElementById(
            "aiChatForm"
        );

    if (
        !toggle ||
        !close ||
        !box ||
        !form
    ) {
        return;
    }

    toggle.addEventListener(
        "click",
        async () => {

            box.classList.toggle(
                "d-none"
            );

            const isOpen =
                !box.classList.contains(
                    "d-none"
                );

            if (
                isOpen &&
                !aiChatInitialized
            ) {

                await initializeAIChat();

            }

        }
    );


    close.addEventListener(
        "click",
        () => {

            box.classList.add(
                "d-none"
            );

        }
    );


    form.addEventListener(
        "submit",
        handleAISubmit
    );

}


async function initializeAIChat() {

    aiChatInitialized = true;

    try {

        const storedSessionId =
            sessionStorage.getItem(
                "ai_chat_session_id"
            );

        if (storedSessionId) {

            aiChatSessionId =
                Number(
                    storedSessionId
                );

            const loaded =
                await loadAIHistory();

            if (loaded) {
                return;
            }

        }

        await createAISession();

    }
    catch (error) {

        console.error(error);

        addAIMessage(
            "assistant",
            "Không thể kết nối AI. " +
            "Bạn vui lòng thử lại sau."
        );

    }

}


async function createAISession() {

    const response =
        await apiFetch(
            "/api/chat/sessions",
            {
                method: "POST",
            }
        );

    const data =
        await parseApiResponse(
            response
        );

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tạo phiên AI."
        );

    }

    aiChatSessionId =
        data.session_id;

    sessionStorage.setItem(
        "ai_chat_session_id",
        String(
            aiChatSessionId
        )
    );

}


async function loadAIHistory() {

    const response =
        await apiFetch(
            `/api/chat/sessions/${aiChatSessionId}/messages`
        );

    if (response.status === 404) {

        sessionStorage.removeItem(
            "ai_chat_session_id"
        );

        aiChatSessionId = null;

        return false;
    }

    const data =
        await parseApiResponse(
            response
        );

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải lịch sử chat."
        );

    }

    const messages =
        Array.isArray(data)
            ? data
            : [];

    const container =
        document.getElementById(
            "aiChatMessages"
        );

    container.innerHTML = "";

    messages.forEach(
        message => {

            addAIMessage(
                message.sender_type
                    === "Patient"
                    ? "user"
                    : "assistant",

                message.content
            );

        }
    );

    return true;

}


async function handleAISubmit(
    event
) {

    event.preventDefault();

    const input =
        document.getElementById(
            "aiChatInput"
        );

    const sendButton =
        document.getElementById(
            "aiChatSend"
        );

    const content =
        input.value.trim();

    if (!content) {
        return;
    }

    if (!aiChatSessionId) {

        await initializeAIChat();

        if (!aiChatSessionId) {
            return;
        }

    }

    addAIMessage(
        "user",
        content
    );

    input.value = "";

    input.disabled = true;
    sendButton.disabled = true;

    const typing =
        addTypingMessage();

    try {

        const response =
            await apiFetch(
                `/api/chat/sessions/${aiChatSessionId}/messages`,
                {
                    method: "POST",

                    body: JSON.stringify({
                        content: content,
                    }),
                }
            );

        const data =
            await parseApiResponse(
                response
            );

        typing.remove();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể gửi tin nhắn."
            );

        }

        addAIMessage(
            "assistant",
            data.reply
        );

    }
    catch (error) {

        typing.remove();

        console.error(error);

        addAIMessage(
            "assistant",
            error.message ||
            "Có lỗi xảy ra. Bạn vui lòng thử lại."
        );

    }
    finally {

        input.disabled = false;
        sendButton.disabled = false;

        input.focus();

    }

}


function addAIMessage(
    role,
    content
) {

    const container =
        document.getElementById(
            "aiChatMessages"
        );

    const message =
        document.createElement(
            "div"
        );

    message.className =
        role === "user"
            ? "ai-message user"
            : "ai-message";


    const avatar =
        document.createElement(
            "div"
        );

    avatar.className =
        "ai-message-avatar";

    avatar.innerHTML =
        role === "user"
            ? `<i class="bi bi-person-fill"></i>`
            : `<i class="bi bi-robot"></i>`;


    const contentBox =
        document.createElement(
            "div"
        );

    contentBox.className =
        "ai-message-content";

    contentBox.textContent =
        content;


    message.appendChild(
        avatar
    );

    message.appendChild(
        contentBox
    );

    container.appendChild(
        message
    );

    scrollAIChatToBottom();

    return message;

}


function addTypingMessage() {

    return addAIMessage(
        "assistant",
        "AI đang xử lý..."
    );

}


function scrollAIChatToBottom() {

    const container =
        document.getElementById(
            "aiChatMessages"
        );

    if (!container) {
        return;
    }

    container.scrollTop =
        container.scrollHeight;

}