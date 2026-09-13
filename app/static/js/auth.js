const PUBLIC_PATHS = [
    "/",
    "/login",
    "/register",
];


const ROLE_ROUTES = {

    Admin:
        "/dashboard",

    Receptionist:
        "/receptionist/dashboard",

    Doctor:
        "/doctor/dashboard",

    Patient:
        "/patient/dashboard",

};


function getCurrentUser() {

    const raw =
        sessionStorage.getItem(
            "current_user"
        );


    if (!raw) {
        return null;
    }


    try {

        return JSON.parse(
            raw
        );

    }
    catch (error) {

        console.error(
            "Không thể đọc current_user:",
            error
        );

        return null;

    }

}


function setCurrentUser(
    user
) {

    sessionStorage.setItem(
        "current_user",
        JSON.stringify(user)
    );

}


function redirectByRole(
    role
) {

    const route =
        ROLE_ROUTES[role];


    window.location.href =
        route || "/login";

}


function logout() {

    clearAccessToken();

    window.location.href =
        "/login";

}


function isPublicPath() {

    return PUBLIC_PATHS.includes(
        window.location.pathname
    );

}


function getRequiredRole(
    pathname
) {

    if (
        pathname ===
        "/dashboard"
        ||
        pathname.startsWith(
            "/dashboard/"
        )
    ) {

        return "Admin";

    }


    if (
        pathname ===
        "/receptionist"
        ||
        pathname.startsWith(
            "/receptionist/"
        )
    ) {

        return "Receptionist";

    }


    if (
        pathname ===
        "/doctor"
        ||
        pathname.startsWith(
            "/doctor/"
        )
    ) {

        return "Doctor";

    }


    if (
        pathname ===
        "/patient"
        ||
        pathname.startsWith(
            "/patient/"
        )
    ) {

        return "Patient";

    }


    return null;

}


async function loadCurrentUser() {

    const cachedUser =
        getCurrentUser();


    if (cachedUser) {

        return cachedUser;

    }


    if (!isAuthenticated()) {

        return null;

    }


    const response =
        await fetch(
            "/api/auth/me",
            {
                method: "GET",

                headers: {

                    Accept:
                        "application/json",

                    Authorization:
                        `Bearer ${getAccessToken()}`,

                },

            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        clearAccessToken();

        return null;

    }


    setCurrentUser(
        data
    );


    return data;

}


async function protectPrivatePage() {

    const pathname =
        window.location.pathname;


    if (isPublicPath()) {

        return;

    }


    const requiredRole =
        getRequiredRole(
            pathname
        );


    /*
     * Route không nằm trong nhóm
     * private mà mình định nghĩa.
     */
    if (!requiredRole) {

        return;

    }


    /*
     * Chưa có token
     * → về login.
     */
    if (!isAuthenticated()) {

        window.location.href =
            "/login";

        return;

    }


    try {

        const currentUser =
            await loadCurrentUser();


        if (!currentUser) {

            window.location.href =
                "/login";

            return;

        }


        /*
         * Có token nhưng role không
         * phù hợp với URL hiện tại.
         */
        if (
            currentUser.role !==
            requiredRole
        ) {

            redirectByRole(
                currentUser.role
            );

        }

    }
    catch (error) {

        console.error(
            "Lỗi kiểm tra quyền truy cập:",
            error
        );

        clearAccessToken();

        window.location.href =
            "/login";

    }

}


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        /*
         * Bảo vệ private routes.
         */
        await protectPrivatePage();


        /*
         * Các nút logout.
         */
        document
            .querySelectorAll(
                "#logoutLink, #dropdownLogout"
            )
            .forEach(
                (
                    element
                ) => {

                    element.addEventListener(
                        "click",
                        (
                            event
                        ) => {

                            event.preventDefault();

                            logout();

                        }
                    );

                }
            );

    }
);