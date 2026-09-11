let currentPatient = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            await loadProfile();

            setupProfileForm();

        }
        catch (error) {

            console.error(
                error
            );

            showProfileAlert(
                error.message ||
                "Không thể tải hồ sơ.",
                "danger"
            );

        }

    }
);


async function loadProfile() {

    const response =
        await apiFetch(
            "/api/patient/me"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải hồ sơ."
        );

    }


    currentPatient =
        data;


    renderProfile(
        data
    );

}


function renderProfile(
    patient
) {

    const name =
        patient.full_name ||
        patient.username ||
        "Bệnh nhân";


    document.getElementById(
        "profileName"
    ).textContent =
        name;


    document.getElementById(
        "profileUsername"
    ).textContent =
        `@${patient.username}`;


    document.getElementById(
        "profileAvatar"
    ).textContent =
        getInitials(name);


    document.getElementById(
        "fullName"
    ).value =
        patient.full_name || "";


    document.getElementById(
        "email"
    ).value =
        patient.email || "";


    document.getElementById(
        "phone"
    ).value =
        patient.phone || "";


    document.getElementById(
        "dob"
    ).value =
        patient.dob || "";


    document.getElementById(
        "gender"
    ).value =
        patient.gender || "";


    document.getElementById(
        "address"
    ).value =
        patient.address || "";


    document.getElementById(
        "sidebarUserName"
    ).textContent =
        name;


    document.getElementById(
        "topUserName"
    ).textContent =
        name;


    document.getElementById(
        "userAvatar"
    ).textContent =
        getInitials(name);

}


function setupProfileForm() {

    document.getElementById(
        "profileForm"
    ).addEventListener(
        "submit",
        saveProfile
    );

}


async function saveProfile(
    event
) {

    event.preventDefault();


    const button =
        document.getElementById(
            "saveProfileButton"
        );


    const payload = {

        full_name:
            document.getElementById(
                "fullName"
            ).value.trim(),

        email:
            document.getElementById(
                "email"
            ).value.trim() || null,

        phone:
            document.getElementById(
                "phone"
            ).value.trim() || null,

        dob:
            document.getElementById(
                "dob"
            ).value || null,

        gender:
            document.getElementById(
                "gender"
            ).value || null,

        address:
            document.getElementById(
                "address"
            ).value.trim() || null,

    };


    button.disabled =
        true;


    try {

        const response =
            await apiFetch(
                "/api/patient/me",
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
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

            throw new Error(
                data.detail ||
                "Cập nhật hồ sơ thất bại."
            );

        }


        currentPatient =
            data;


        renderProfile(
            data
        );


        showProfileAlert(
            "Cập nhật hồ sơ thành công.",
            "success"
        );

    }
    catch (error) {

        console.error(
            error
        );


        showProfileAlert(
            error.message ||
            "Không thể cập nhật hồ sơ.",
            "danger"
        );

    }
    finally {

        button.disabled =
            false;

    }

}


function showProfileAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "profileAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );


    window.scrollTo({
        top: 0,
        behavior: "smooth",
    });

}