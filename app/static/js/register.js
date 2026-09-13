document.addEventListener(
    "DOMContentLoaded",
    () => {

        if (isAuthenticated()){
            const currentUser = getCurrentUser();

            if (currentUser){
                redirectByRole(currentUser.role);

                return;
            }
        }

        const form =
            document.getElementById(
                "registerForm"
            );


        const alertBox =
            document.getElementById(
                "registerAlert"
            );


        const button =
            document.getElementById(
                "registerButton"
            );


        const buttonText =
            document.getElementById(
                "registerButtonText"
            );


        const spinner =
            document.getElementById(
                "registerSpinner"
            );


        const passwordInput =
            document.getElementById(
                "password"
            );


        const confirmPasswordInput =
            document.getElementById(
                "confirmPassword"
            );


        const togglePassword =
            document.getElementById(
                "togglePassword"
            );


        const toggleConfirmPassword =
            document.getElementById(
                "toggleConfirmPassword"
            );


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


        function toggleInputType(
            input,
            buttonElement
        ) {

            const isPassword =
                input.type === "password";


            input.type =
                isPassword
                    ? "text"
                    : "password";


            buttonElement.innerHTML =
                isPassword
                    ? '<i class="bi bi-eye-slash"></i>'
                    : '<i class="bi bi-eye"></i>';

        }


        togglePassword.addEventListener(
            "click",
            () => {

                toggleInputType(
                    passwordInput,
                    togglePassword
                );

            }
        );


        toggleConfirmPassword.addEventListener(
            "click",
            () => {

                toggleInputType(
                    confirmPasswordInput,
                    toggleConfirmPassword
                );

            }
        );


        form.addEventListener(
            "submit",
            async (event) => {

                event.preventDefault();

                clearAlert();


                const username =
                    document
                        .getElementById(
                            "username"
                        )
                        .value
                        .trim();


                const password =
                    passwordInput.value;


                const confirmPassword =
                    confirmPasswordInput.value;


                const fullName =
                    document
                        .getElementById(
                            "fullName"
                        )
                        .value
                        .trim();


                const email =
                    document
                        .getElementById(
                            "email"
                        )
                        .value
                        .trim();


                const phone =
                    document
                        .getElementById(
                            "phone"
                        )
                        .value
                        .trim();


                const dob =
                    document
                        .getElementById(
                            "dob"
                        )
                        .value;


                const gender =
                    document
                        .getElementById(
                            "gender"
                        )
                        .value;


                const address =
                    document
                        .getElementById(
                            "address"
                        )
                        .value
                        .trim();


                if (!fullName) {

                    showAlert(
                        "Vui lòng nhập họ và tên."
                    );

                    return;

                }


                if (username.length < 6) {

                    showAlert(
                        "Tên đăng nhập phải có ít nhất 6 ký tự."
                    );

                    return;

                }


                if (!/[A-Za-zÀ-ỹ]/.test(username)) {

                    showAlert(
                        "Tên đăng nhập phải có ít nhất 1 chữ cái."
                    );

                    return;

                }


                if (!/\d/.test(username)) {

                    showAlert(
                        "Tên đăng nhập phải có ít nhất 1 chữ số."
                    );

                    return;

                }


                if (password.length < 6) {

                    showAlert(
                        "Mật khẩu phải có ít nhất 6 ký tự."
                    );

                    return;

                }


                if (!/\d/.test(password)) {

                    showAlert(
                        "Mật khẩu phải có ít nhất 1 chữ số."
                    );

                    return;

                }


                if (
                    password !==
                    confirmPassword
                ) {

                    showAlert(
                        "Mật khẩu xác nhận không khớp."
                    );

                    return;

                }


                if (
                    phone &&
                    !/^\d+$/.test(phone)
                ) {

                    showAlert(
                        "Số điện thoại chỉ được chứa chữ số."
                    );

                    return;

                }


                if (
                    email &&
                    !email.includes("@")
                ) {

                    showAlert(
                        "Email không hợp lệ."
                    );

                    return;

                }


                const payload = {

                    username,

                    password,

                    confirm_password:
                        confirmPassword,

                    full_name:
                        fullName,

                    email:
                        email || null,

                    phone:
                        phone || null,

                    dob:
                        dob || null,

                    gender:
                        gender || null,

                    address:
                        address || null,

                };


                setLoading(true);


                try {

                    const response =
                        await fetch(
                            "/api/auth/register",
                            {
                                method: "POST",

                                headers: {

                                    "Content-Type":
                                        "application/json",

                                    "Accept":
                                        "application/json",

                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    ),

                            }
                        );


                    const data =
                        await parseApiResponse(
                            response
                        );


                    if (!response.ok) {

                        let message =
                            "Đăng ký không thành công.";


                        if (
                            typeof data ===
                            "object"
                        ) {

                            if (
                                Array.isArray(
                                    data.detail
                                )
                            ) {

                                message =
                                    data.detail
                                        .map(
                                            item =>
                                                item.msg
                                        )
                                        .join(
                                            "; "
                                        );

                            }
                            else if (
                                data.detail
                            ) {

                                message =
                                    data.detail;

                            }

                        }


                        showAlert(
                            message
                        );

                        return;

                    }


                    showAlert(
                        "Đăng ký thành công. Đang chuyển tới trang đăng nhập...",
                        "success"
                    );


                    form.reset();


                    setTimeout(
                        () => {

                            window.location.href =
                                "/login";

                        },
                        1000
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

                    setLoading(false);

                }

            }
        );

    }
);