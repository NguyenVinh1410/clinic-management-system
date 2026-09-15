const API_BASE_URL = "";

function getAccessToken(){
    return sessionStorage.getItem("access_token");
}

function setAccessToken(token){
    sessionStorage.setItem("access_token", token)
}

function clearAccessToken(){
    sessionStorage.removeItem("access_token");

    sessionStorage.removeItem("current_user");

    sessionStorage.removeItem("ai_chat_session_id");
}

function isAuthenticated(){
    return Boolean(getAccessToken());
}

async function apiFetch(url, options = {}){
    const token = getAccessToken();

    const headers = new Headers(options.headers || {});

    headers.set(
        "Accept",
        "application/json"
    );

    if(
        options.body &&
        !(options.body instanceof FormData) &&
        !headers.has("Content-Type")
    ) {
        headers.set(
            "Content-Type",
            "application/json"
        );
    }

    if(token){
        headers.set(
            "Authorization",
            `Bearer ${token}`
        );
    }

    const response =
        await fetch(
            `${API_BASE_URL}${url}`,
            {
                ...options,
                headers
            }
        );

    if (response.status === 401){
        clearAccessToken();

        const pathname = window.location.pathname;

        if (pathname !== "/login" && pathname !== "/register"){
            window.location.href = "/login";
        }

    }
    return response;
}

async function parseApiResponse(
    response
) {

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";

    if (
        !contentType.includes(
            "application/json"
        )
    ) {
        return response.text();
    }

    const data =
        await response.json();

    if (
        Array.isArray(
            data?.detail
        )
    ) {

        data.validation_errors =
            data.detail;

        data.detail =
            data.detail
                .map(item => {

                    if (
                        typeof item ===
                        "string"
                    ) {
                        return item;
                    }

                    if (item?.msg) {
                        return item.msg;
                    }

                    return (
                        "Dữ liệu không hợp lệ."
                    );
                })
                .join("; ");
    }

    else if (
        data?.detail &&
        typeof data.detail ===
        "object"
    ) {

        data.detail =
            data.detail.msg ||
            data.detail.message ||
            JSON.stringify(
                data.detail
            );
    }

    return data;
}