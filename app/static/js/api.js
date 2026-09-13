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

async function parseApiResponse(response){
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")){
        return response.json();
    }

    return response.text();
}

function formatCurrency(value) {
    return new Intl.NumberFormat(
        "vi-VN",
        {
            style: "currency",
            currency: "VND",
            maximumFractionDigits: 0,
        }
    ).format(Number(value || 0));
}

function escapeHtml(value) {

    return String(
        value ?? ""
    )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}