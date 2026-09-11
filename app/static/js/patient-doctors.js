let allDoctors = [];
let allSpecialties = [];


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            await Promise.all([
                loadPatientHeader(),
                loadSpecialties(),
                loadDoctors(),
            ]);


            setupDoctorFilters();

        }
        catch (error) {

            console.error(
                error
            );

        }

    }
);


async function loadPatientHeader() {

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
            data.detail
        );

    }


    const name =
        data.full_name ||
        data.username;


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


async function loadSpecialties() {

    const response =
        await apiFetch(
            "/api/specialty"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail
        );

    }


    allSpecialties = data;


    const select =
        document.getElementById(
            "specialtyFilter"
        );


    allSpecialties.forEach(
        specialty => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                specialty.specialty_id;


            option.textContent =
                specialty.name;


            select.appendChild(
                option
            );

        }
    );

}


async function loadDoctors() {

    const response =
        await apiFetch(
            "/api/doctor"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail
        );

    }


    allDoctors = data;

    renderDoctors(
        allDoctors
    );

}


function renderDoctors(
    doctors
) {

    const container =
        document.getElementById(
            "doctorList"
        );


    if (
        !doctors ||
        doctors.length === 0
    ) {

        container.innerHTML = `
            <div class="col-12">

                <div class="content-card">

                    <div class="text-center py-5 text-secondary">

                        <i class="bi bi-person-x fs-1 d-block mb-3"></i>

                        Không tìm thấy bác sĩ.

                    </div>

                </div>

            </div>
        `;

        return;

    }


    container.innerHTML =
        doctors
            .map(
                doctor => `

                    <div
                        class="col-12 col-md-6 col-xl-4">

                        <div
                            class="patient-doctor-card p-3">

                            <div
                                class="d-flex align-items-start gap-3">

                                <div
                                    class="doctor-avatar">

                                    <i class="bi bi-person-fill"></i>

                                </div>


                                <div
                                    class="flex-grow-1">

                                    <h5
                                        class="fw-bold mb-1">

                                        ${escapeHtml(
                                            doctor.full_name
                                        )}

                                    </h5>


                                    <div
                                        class="small text-primary fw-semibold mb-2">

                                        ${getSpecialtyName(
                                            doctor.specialty_id
                                        )}

                                    </div>


                                    <div
                                        class="small text-secondary mb-1">

                                        <i class="bi bi-mortarboard me-1"></i>

                                        ${escapeHtml(
                                            doctor.qualification ||
                                            "Chưa cập nhật"
                                        )}

                                    </div>

                                </div>

                            </div>


                            <div class="d-flex gap-2 mt-3">

                                <a
                                    href="/patient/doctors/${doctor.user_id}"
                                    class="btn btn-sm btn-light flex-grow-1">

                                    Xem hồ sơ

                                </a>


                                <a
                                    href="/patient/book-appointment?doctor_id=${doctor.user_id}"
                                    class="btn btn-sm btn-primary">

                                    Đặt lịch

                                </a>

                            </div>

                        </div>

                    </div>

                `
            )
            .join("");

}


function setupDoctorFilters() {

    const searchInput =
        document.getElementById(
            "doctorSearch"
        );


    const specialtySelect =
        document.getElementById(
            "specialtyFilter"
        );


    function applyFilter() {

        const keyword =
            searchInput.value
                .trim()
                .toLowerCase();


        const specialtyId =
            specialtySelect.value;


        const filtered =
            allDoctors.filter(
                doctor => {

                    const matchName =
                        !keyword ||
                        doctor.full_name
                            .toLowerCase()
                            .includes(
                                keyword
                            );


                    const matchSpecialty =
                        !specialtyId ||
                        String(
                            doctor.specialty_id
                        ) ===
                        specialtyId;


                    return (
                        matchName &&
                        matchSpecialty
                    );

                }
            );


        renderDoctors(
            filtered
        );

    }


    searchInput.addEventListener(
        "input",
        applyFilter
    );


    specialtySelect.addEventListener(
        "change",
        applyFilter
    );

}


function getSpecialtyName(
    specialtyId
) {

    const specialty =
        allSpecialties.find(
            item =>
                item.specialty_id ===
                specialtyId
        );


    return specialty
        ? specialty.name
        : "Chưa cập nhật";

}