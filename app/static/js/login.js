document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "loginForm"
            );


        const usernameInput =
            document.getElementById(
                "username"
            );


        const passwordInput =
            document.getElementById(
                "password"
            );


        const alertBox =
            document.getElementById(
                "loginAlert"
            );


        const button =
            document.getElementById(
                "loginButton"
            );


        const buttonText =
            document.getElementById(
                "loginButtonText"
            );


        const spinner =
            document.getElementById(
                "loginSpinner"
            );


        const togglePassword =
            document.getElementById(
                "togglePassword"
            );


        if (isAuthenticated()) {

            window.location.href =
                "/dashboard";

            return;

        }


        function showAlert(
            message,
            type = "danger"
        ) {

            alertBox.className =
                `alert alert-${type}`;

            alertBox.textContent =
                message;

            alertBox.classList.remove(
                "d-none"
            );

        }


        function clearAlert() {

            alertBox.className =
                "alert d-none";

            alertBox.textContent =
                "";

        }


        function setLoading(
            loading
        ) {

            button.disabled =
                loading;

            buttonText.classList.toggle(
                "d-none",
                loading
            );

            spinner.classList.toggle(
                "d-none",
                !loading
            );

        }


        togglePassword.addEventListener(
            "click",
            () => {

                const isPassword =
                    passwordInput.type ===
                    "password";


                passwordInput.type =
                    isPassword
                        ? "text"
                        : "password";


                togglePassword.innerHTML =
                    isPassword
                        ? '<i class="bi bi-eye-slash"></i>'
                        : '<i class="bi bi-eye"></i>';

            }
        );


        form.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                clearAlert();


                const username =
                    usernameInput.value.trim();


                const password =
                    passwordInput.value;


                if (
                    !username ||
                    !password
                ) {

                    showAlert(
                        "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu."
                    );

                    return;

                }


                setLoading(true);


                try {

                    const body =
                        new URLSearchParams({
                            username,
                            password,
                        });


                    const response =
                        await fetch(
                            "/api/auth/login",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/x-www-form-urlencoded",

                                    "Accept":
                                        "application/json",
                                },

                                body,
                            }
                        );


                    const data =
                        await parseApiResponse(
                            response
                        );


                    if (!response.ok) {

                        showAlert(
                            typeof data === "object"
                                ? data.detail ||
                                  "Đăng nhập không thành công."
                                : "Đăng nhập không thành công."
                        );

                        return;

                    }


                    setAccessToken(
                        data.access_token
                    );


                    const meResponse =
                        await apiFetch(
                            "/api/auth/me"
                        );


                    const meData =
                        await parseApiResponse(
                            meResponse
                        );


                    if (!meResponse.ok) {

                        clearAccessToken();

                        showAlert(
                            "Đăng nhập thành công nhưng không lấy được thông tin tài khoản."
                        );

                        return;

                    }


                    sessionStorage.setItem(
                        "current_user",
                        JSON.stringify(meData)
                    );


                    redirectByRole(
                        meData.role
                    );

                }
                catch (error) {

                    console.error(
                        error
                    );

                    showAlert(
                        "Không thể kết nối tới máy chủ."
                    );

                }
                finally {

                    setLoading(
                        false
                    );

                }

            }
        );

    }
);