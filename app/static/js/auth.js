function redirectByRole(role) {
    const routes = {
        Admin: "/dashboard",

        Receptionist: "/receptionist/dashboard",

        Doctor: "/dashboard",

        Patient: "/patient/dashboard",
    };

    window.location.href = routes[role] || "/login";
}

function logout() {

    clearAccessToken();

    window.location.href =
        "/login";

}

document.addEventListener(
    "DOMContentLoaded",
    () => {

        document
            .querySelectorAll(
                "#logoutLink, #dropdownLogout"
            )
            .forEach(
                (element) => {

                    element.addEventListener(
                        "click",
                        (event) => {

                            event.preventDefault();

                            logout();

                        }
                    );

                }
            );

    }
);