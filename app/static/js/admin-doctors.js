let doctors = [];
let specialties = [];


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            await loadCurrentUser();

            await loadSpecialties();

            await loadDoctors();

            setupFilters();

            setupRefresh();

            setupDoctorCreateForm();

        }
        catch (error) {

            console.error(
                error
            );

            showDoctorAlert(
                error.message ||
                "Không thể tải dữ liệu bác sĩ.",
                "danger"
            );

        }

    }
);


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
            data.detail ||
            "Không thể tải chuyên khoa."
        );

    }


    specialties =
        Array.isArray(data)
            ? data
            : data.items || [];


    const filterSelect =
        document.getElementById(
            "specialtyFilter"
        );


    if (filterSelect) {

        filterSelect.innerHTML = `
            <option value="">
                Tất cả chuyên khoa
            </option>
        `;


        specialties.forEach(
            specialty => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    specialty.specialty_id;


                option.textContent =
                    specialty.name;


                filterSelect.appendChild(
                    option
                );

            }
        );

    }


    const createSelect =
        document.getElementById(
            "createDoctorSpecialty"
        );


    if (createSelect) {

        createSelect.innerHTML = `
            <option value="">
                Chọn chuyên khoa
            </option>
        `;


        specialties.forEach(
            specialty => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    specialty.specialty_id;


                option.textContent =
                    specialty.name;


                createSelect.appendChild(
                    option
                );

            }
        );

    }

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
            data.detail ||
            "Không thể tải danh sách bác sĩ."
        );

    }


    doctors =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderDoctors(
        doctors
    );

}


function renderDoctors(
    items
) {

    const tbody =
        document.getElementById(
            "doctorList"
        );


    if (!tbody) {

        return;

    }


    if (!items.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="5"
                    class="text-center
                           py-5
                           text-secondary">

                    Không tìm thấy bác sĩ.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        items
            .map(
                doctor => {

                    const specialty =
                        specialties.find(
                            item =>
                                Number(
                                    item.specialty_id
                                ) ===
                                Number(
                                    doctor.specialty_id
                                )
                        );


                    const statusBadge =
                        doctor.status ===
                        "Active"

                            ? `
                                <span
                                    class="badge
                                           text-bg-success">

                                    Hoạt động

                                </span>
                            `

                            : `
                                <span
                                    class="badge
                                           text-bg-secondary">

                                    Đã khóa

                                </span>
                            `;


                    const actionButton =
                        doctor.status ===
                        "Active"

                            ? `
                                <button
                                    type="button"
                                    class="btn
                                           btn-sm
                                           btn-outline-danger"
                                    data-lock-doctor="${doctor.user_id}">

                                    <i
                                        class="bi bi-lock">
                                    </i>

                                </button>
                            `

                            : `
                                <span
                                    class="text-secondary
                                           small">

                                    Đã khóa

                                </span>
                            `;


                    return `
                        <tr>

                            <td>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        doctor.full_name ||
                                        ""
                                    )}

                                </div>

                                <div
                                    class="small
                                           text-secondary">

                                    ${escapeHtml(
                                        doctor.username ||
                                        ""
                                    )}

                                </div>

                            </td>


                            <td>

                                ${escapeHtml(
                                    specialty?.name ||
                                    "Chưa cập nhật"
                                )}

                            </td>


                            <td>

                                ${escapeHtml(
                                    doctor.qualification ||
                                    "Chưa cập nhật"
                                )}

                            </td>


                            <td>

                                ${statusBadge}

                            </td>


                            <td class="text-end">

                                <div
                                    class="d-flex
                                           justify-content-end
                                           gap-2">

                                    <button
                                        type="button"
                                        class="btn
                                               btn-sm
                                               btn-outline-primary"
                                        data-edit-doctor="${doctor.user_id}">

                                        <i
                                            class="bi bi-pencil">
                                        </i>

                                    </button>


                                    ${actionButton}

                                </div>

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");


    bindDoctorActions();

}


function bindDoctorActions() {

    document
        .querySelectorAll(
            "[data-edit-doctor]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const doctorId =
                            Number(
                                button.dataset.editDoctor
                            );


                        editDoctor(
                            doctorId
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-lock-doctor]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        const doctorId =
                            Number(
                                button.dataset.lockDoctor
                            );


                        deactivateDoctor(
                            doctorId
                        );

                    }
                );

            }
        );

}


async function editDoctor(
    doctorId
) {

    const doctor =
        doctors.find(
            item =>
                Number(
                    item.user_id
                ) ===
                Number(
                    doctorId
                )
        );


    if (!doctor) {

        showDoctorAlert(
            "Không tìm thấy bác sĩ.",
            "danger"
        );

        return;

    }


    const qualification =
        window.prompt(
            "Bằng cấp / chứng chỉ:",
            doctor.qualification || ""
        );


    if (qualification === null) {

        return;

    }


    const response =
        await apiFetch(
            `/api/doctor/${doctorId}`,
            {

                method: "PATCH",

                body:
                    JSON.stringify({

                        qualification:
                            qualification
                                .trim() ||
                            null,

                    }),

            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể cập nhật bác sĩ."
        );

    }


    showDoctorAlert(
        "Đã cập nhật thông tin bác sĩ.",
        "success"
    );


    await loadDoctors();

}


async function deactivateDoctor(
    doctorId
) {

    const confirmed =
        window.confirm(
            "Bạn có chắc muốn khóa bác sĩ này?"
        );


    if (!confirmed) {

        return;

    }


    const response =
        await apiFetch(
            `/api/doctor/${doctorId}`,
            {
                method: "DELETE",
            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể khóa bác sĩ."
        );

    }


    showDoctorAlert(
        "Đã khóa bác sĩ.",
        "success"
    );


    await loadDoctors();

}


function setupFilters() {

    const searchInput =
        document.getElementById(
            "doctorSearch"
        );


    const specialtyFilter =
        document.getElementById(
            "specialtyFilter"
        );


    function applyFilters() {

        const keyword =
            searchInput.value
                .trim()
                .toLowerCase();


        const specialtyId =
            specialtyFilter.value;


        const filtered =
            doctors.filter(
                doctor => {

                    const name =
                        String(
                            doctor.full_name ||
                            ""
                        )
                            .toLowerCase();


                    const matchName =
                        !keyword ||
                        name.includes(
                            keyword
                        );


                    const matchSpecialty =
                        !specialtyId ||
                        String(
                            doctor.specialty_id
                        ) ===
                        String(
                            specialtyId
                        );


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
        applyFilters
    );


    specialtyFilter.addEventListener(
        "change",
        applyFilters
    );

}


function setupRefresh() {

    const button =
        document.getElementById(
            "refreshDoctors"
        );


    button?.addEventListener(
        "click",
        async () => {

            try {

                await loadSpecialties();

                await loadDoctors();

            }
            catch (error) {

                showDoctorAlert(
                    error.message,
                    "danger"
                );

            }

        }
    );

}


function showDoctorAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "doctorAlert"
        );


    if (!alert) {

        return;

    }


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );


    setTimeout(
        () => {

            alert.classList.add(
                "d-none"
            );

        },
        4000
    );

}

function setupDoctorCreateForm() {

    const form =
        document.getElementById(
            "doctorCreateForm"
        );


    if (!form) {

        return;

    }


    form.addEventListener(
        "submit",
        createDoctor
    );

}

async function createDoctor(
    event
) {

    event.preventDefault();


    const username =
        document
            .getElementById(
                "createDoctorUsername"
            )
            .value
            .trim();


    const password =
        document
            .getElementById(
                "createDoctorPassword"
            )
            .value;


    const fullName =
        document
            .getElementById(
                "createDoctorFullName"
            )
            .value
            .trim();


    const email =
        document
            .getElementById(
                "createDoctorEmail"
            )
            .value
            .trim();


    const phone =
        document
            .getElementById(
                "createDoctorPhone"
            )
            .value
            .trim();


    const gender =
        document
            .getElementById(
                "createDoctorGender"
            )
            .value;


    const specialtyId =
        document
            .getElementById(
                "createDoctorSpecialty"
            )
            .value;


    const qualification =
        document
            .getElementById(
                "createDoctorQualification"
            )
            .value
            .trim();


    const bio =
        document
            .getElementById(
                "createDoctorBio"
            )
            .value
            .trim();


    if (!username) {

        showDoctorAlert(
            "Vui lòng nhập username.",
            "danger"
        );

        return;

    }


    if (!password) {

        showDoctorAlert(
            "Vui lòng nhập mật khẩu.",
            "danger"
        );

        return;

    }


    if (!fullName) {

        showDoctorAlert(
            "Vui lòng nhập họ tên bác sĩ.",
            "danger"
        );

        return;

    }


    if (!specialtyId) {

        showDoctorAlert(
            "Vui lòng chọn chuyên khoa.",
            "danger"
        );

        return;

    }


    const payload = {

        username:
            username,

        password:
            password,

        full_name:
            fullName,

        email:
            email || null,

        phone:
            phone || null,

        gender:
            gender || null,

        role:
            "Doctor",

        specialty_id:
            Number(
                specialtyId
            ),

        qualification:
            qualification ||
            null,

        bio:
            bio ||
            null,

    };


    const response =
        await apiFetch(
            "/api/users",
            {

                method:
                    "POST",

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
            "Không thể tạo tài khoản bác sĩ."
        );

    }


    showDoctorAlert(
        "Đã tạo tài khoản bác sĩ thành công.",
        "success"
    );


    document
        .getElementById(
            "doctorCreateForm"
        )
        .reset();


    const modalElement =
        document.getElementById(
            "doctorCreateModal"
        );


    const modal =
        bootstrap.Modal.getInstance(
            modalElement
        );


    modal?.hide();


    await loadDoctors();

}