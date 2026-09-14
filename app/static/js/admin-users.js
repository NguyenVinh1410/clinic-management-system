let users = [];
let specialties = [];


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {
            window.location.href = "/login";
            return;
        }

        try {

            const currentUser =
                await loadCurrentUser();

            if (currentUser.role !== "Admin") {
                window.location.href = "/login";
                return;
            }

            await loadSpecialties();
            await loadUsers();

            setupEvents();

        }
        catch (error) {

            console.error(error);

            showUserAlert(
                error.message ||
                "Không thể tải dữ liệu.",
                "danger"
            );

        }

    }
);


async function loadUsers() {

    const role =
        document.getElementById(
            "roleFilter"
        )?.value || "";

    const url =
        role
            ? `/api/users?role=${encodeURIComponent(role)}`
            : "/api/users";

    const response =
        await apiFetch(url);

    const data =
        await parseApiResponse(response);

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải danh sách người dùng."
        );

    }

    users =
        Array.isArray(data)
            ? data
            : data.items || [];

    renderUsers(users);
}


async function loadSpecialties() {

    const response =
        await apiFetch(
            "/api/specialty"
        );

    const data =
        await parseApiResponse(response);

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

    fillSpecialtySelect(
        document.getElementById(
            "createSpecialty"
        )
    );

    fillSpecialtySelect(
        document.getElementById(
            "editSpecialty"
        )
    );
}


function fillSpecialtySelect(select) {

    if (!select) {
        return;
    }

    select.innerHTML = `
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

            select.appendChild(option);

        }
    );
}


function renderUsers(items) {

    const tbody =
        document.getElementById(
            "userList"
        );

    if (!items.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="text-center py-5 text-secondary">

                    Không tìm thấy người dùng.

                </td>
            </tr>
        `;

        return;
    }

    tbody.innerHTML =
        items
            .map(user => {

                const roleText =
                    getRoleText(user.role);

                const statusHtml =
                    user.status === "Active"
                        ? `
                            <span class="badge text-bg-success">
                                Hoạt động
                            </span>
                        `
                        : `
                            <span class="badge text-bg-secondary">
                                Đã khóa
                            </span>
                        `;

                const actionText =
                    user.status === "Active"
                        ? "Khóa"
                        : "Mở khóa";

                const actionClass =
                    user.status === "Active"
                        ? "btn-outline-danger"
                        : "btn-outline-success";

                return `
                    <tr>

                        <td>

                            <div class="fw-semibold">
                                ${escapeHtml(
                                    user.full_name
                                )}
                            </div>

                        </td>


                        <td>
                            ${escapeHtml(
                                user.username
                            )}
                        </td>


                        <td>
                            <span class="badge text-bg-light border">
                                ${roleText}
                            </span>
                        </td>


                        <td>
                            ${
                                escapeHtml(
                                    user.phone ||
                                    "Chưa cập nhật"
                                )
                            }
                        </td>


                        <td>
                            ${statusHtml}
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
                                    onclick="openEditUser(${user.user_id})">

                                    <i class="bi bi-pencil"></i>

                                    Sửa

                                </button>


                                <button
                                    type="button"
                                    class="btn
                                           btn-sm
                                           ${actionClass}"
                                    onclick="toggleUserStatus(
                                        ${user.user_id},
                                        '${user.status}'
                                    )">

                                    <i class="bi bi-lock"></i>

                                    ${actionText}

                                </button>

                            </div>

                        </td>

                    </tr>
                `;

            })
            .join("");
}


function getRoleText(role) {

    const map = {
        Doctor: "Bác sĩ",
        Receptionist: "Lễ tân",
        Patient: "Bệnh nhân",
    };

    return map[role] || role;
}


function setupEvents() {

    document
        .getElementById("userSearch")
        ?.addEventListener(
            "input",
            applyFilters
        );

    document
        .getElementById("roleFilter")
        ?.addEventListener(
            "change",
            async () => {

                try {
                    await loadUsers();
                }
                catch (error) {

                    showUserAlert(
                        error.message,
                        "danger"
                    );

                }

            }
        );

    document
        .getElementById("refreshUsers")
        ?.addEventListener(
            "click",
            async () => {

                try {
                    await loadUsers();
                }
                catch (error) {

                    showUserAlert(
                        error.message,
                        "danger"
                    );

                }

            }
        );

    document
        .getElementById("createRole")
        ?.addEventListener(
            "change",
            updateCreateRoleFields
        );

    document
        .getElementById("createUserForm")
        ?.addEventListener(
            "submit",
            createUser
        );

    document
        .getElementById("editUserForm")
        ?.addEventListener(
            "submit",
            updateUser
        );
}


function applyFilters() {

    const keyword =
        document
            .getElementById(
                "userSearch"
            )
            ?.value
            .trim()
            .toLowerCase() || "";

    const filtered =
        users.filter(
            user => {

                const name =
                    String(
                        user.full_name || ""
                    ).toLowerCase();

                const username =
                    String(
                        user.username || ""
                    ).toLowerCase();

                const phone =
                    String(
                        user.phone || ""
                    ).toLowerCase();

                return (
                    name.includes(keyword) ||
                    username.includes(keyword) ||
                    phone.includes(keyword)
                );

            }
        );

    renderUsers(filtered);
}


function updateCreateRoleFields() {

    const role =
        document.getElementById(
            "createRole"
        ).value;

    const doctorFields =
        document.getElementById(
            "createDoctorFields"
        );

    const patientFields =
        document.getElementById(
            "createPatientFields"
        );

    doctorFields.classList.toggle(
        "d-none",
        role !== "Doctor"
    );

    patientFields.classList.toggle(
        "d-none",
        role !== "Patient"
    );
}


async function createUser(event) {

    event.preventDefault();

    const role =
        document.getElementById(
            "createRole"
        ).value;

    const payload = {
        username:
            document.getElementById(
                "createUsername"
            ).value.trim(),

        password:
            document.getElementById(
                "createPassword"
            ).value,

        full_name:
            document.getElementById(
                "createFullName"
            ).value.trim(),

        email:
            valueOrNull(
                "createEmail"
            ),

        phone:
            valueOrNull(
                "createPhone"
            ),

        gender:
            valueOrNull(
                "createGender"
            ),

        role: role,
    };

    if (role === "Doctor") {

        payload.specialty_id =
            Number(
                document.getElementById(
                    "createSpecialty"
                ).value
            );

        payload.qualification =
            valueOrNull(
                "createQualification"
            );

        payload.bio =
            valueOrNull(
                "createBio"
            );

    }

    if (role === "Patient") {

        payload.dob =
            valueOrNull(
                "createDob"
            );

        payload.address =
            valueOrNull(
                "createAddress"
            );

    }

    try {

        const response =
            await apiFetch(
                "/api/users",
                {
                    method: "POST",
                    body: JSON.stringify(payload),
                }
            );

        const data =
            await parseApiResponse(response);

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể tạo người dùng."
            );

        }

        showUserAlert(
            "Tạo tài khoản thành công.",
            "success"
        );

        document
            .getElementById(
                "createUserForm"
            )
            .reset();

        updateCreateRoleFields();

        const modal =
            bootstrap.Modal.getInstance(
                document.getElementById(
                    "userCreateModal"
                )
            );

        modal?.hide();

        await loadUsers();

    }
    catch (error) {

        showUserAlert(
            error.message,
            "danger"
        );

    }
}


async function openEditUser(userId) {

    try {

        const response =
            await apiFetch(
                `/api/users/${userId}`
            );

        const user =
            await parseApiResponse(response);

        if (!response.ok) {

            throw new Error(
                user.detail ||
                "Không thể tải người dùng."
            );

        }

        document.getElementById(
            "editUserId"
        ).value = user.user_id;

        document.getElementById(
            "editUsername"
        ).value = user.username || "";

        document.getElementById(
            "editRole"
        ).value =
            getRoleText(user.role);

        document.getElementById(
            "editUserSubtitle"
        ).textContent =
            `${user.full_name} • ${getRoleText(user.role)}`;

        document.getElementById(
            "editFullName"
        ).value = user.full_name || "";

        document.getElementById(
            "editEmail"
        ).value = user.email || "";

        document.getElementById(
            "editPhone"
        ).value = user.phone || "";

        document.getElementById(
            "editGender"
        ).value = user.gender || "";

        document.getElementById(
            "editPassword"
        ).value = "";

        const doctorFields =
            document.getElementById(
                "editDoctorFields"
            );

        const patientFields =
            document.getElementById(
                "editPatientFields"
            );

        doctorFields.classList.toggle(
            "d-none",
            user.role !== "Doctor"
        );

        patientFields.classList.toggle(
            "d-none",
            user.role !== "Patient"
        );

        if (user.role === "Doctor") {

            document.getElementById(
                "editSpecialty"
            ).value =
                user.specialty_id || "";

            document.getElementById(
                "editQualification"
            ).value =
                user.qualification || "";

            document.getElementById(
                "editBio"
            ).value =
                user.bio || "";

        }

        if (user.role === "Patient") {

            document.getElementById(
                "editDob"
            ).value =
                user.dob || "";

            document.getElementById(
                "editAddress"
            ).value =
                user.address || "";

        }

        const modal =
            new bootstrap.Modal(
                document.getElementById(
                    "userEditModal"
                )
            );

        modal.show();

    }
    catch (error) {

        showUserAlert(
            error.message,
            "danger"
        );

    }
}


async function updateUser(event) {

    event.preventDefault();

    const userId =
        document.getElementById(
            "editUserId"
        ).value;

    const role =
        document.getElementById(
            "editRole"
        ).value;

    const roleValue =
        role === "Bác sĩ"
            ? "Doctor"
            : role === "Bệnh nhân"
                ? "Patient"
                : "Receptionist";

    const payload = {

        full_name:
            document.getElementById(
                "editFullName"
            ).value.trim(),

        email:
            valueOrNull(
                "editEmail"
            ),

        phone:
            valueOrNull(
                "editPhone"
            ),

        gender:
            valueOrNull(
                "editGender"
            ),
    };

    const password =
        document.getElementById(
            "editPassword"
        ).value;

    if (password.trim()) {
        payload.password = password;
    }

    if (roleValue === "Doctor") {

        payload.specialty_id =
            Number(
                document.getElementById(
                    "editSpecialty"
                ).value
            );

        payload.qualification =
            valueOrNull(
                "editQualification"
            );

        payload.bio =
            valueOrNull(
                "editBio"
            );

    }

    if (roleValue === "Patient") {

        payload.dob =
            valueOrNull(
                "editDob"
            );

        payload.address =
            valueOrNull(
                "editAddress"
            );

    }

    try {

        const response =
            await apiFetch(
                `/api/users/${userId}`,
                {
                    method: "PATCH",
                    body: JSON.stringify(payload),
                }
            );

        const data =
            await parseApiResponse(response);

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể cập nhật người dùng."
            );

        }

        showUserAlert(
            "Cập nhật tài khoản thành công.",
            "success"
        );

        const modal =
            bootstrap.Modal.getInstance(
                document.getElementById(
                    "userEditModal"
                )
            );

        modal?.hide();

        await loadUsers();

    }
    catch (error) {

        showUserAlert(
            error.message,
            "danger"
        );

    }
}


async function toggleUserStatus(
    userId,
    currentStatus
) {

    const nextStatus =
        currentStatus === "Active"
            ? "Locked"
            : "Active";

    const actionText =
        nextStatus === "Locked"
            ? "khóa"
            : "mở khóa";

    const confirmed =
        window.confirm(
            `Bạn có chắc muốn ${actionText} tài khoản này không?`
        );

    if (!confirmed) {
        return;
    }

    try {

        const response =
            await apiFetch(
                `/api/users/${userId}/status`,
                {
                    method: "PATCH",
                    body: JSON.stringify({
                        status: nextStatus,
                    }),
                }
            );

        const data =
            await parseApiResponse(response);

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Không thể thay đổi trạng thái tài khoản."
            );

        }

        showUserAlert(
            nextStatus === "Locked"
                ? "Đã khóa tài khoản."
                : "Đã mở khóa tài khoản.",
            "success"
        );

        await loadUsers();

    }
    catch (error) {

        showUserAlert(
            error.message,
            "danger"
        );

    }
}


function valueOrNull(id) {

    const value =
        document.getElementById(
            id
        )?.value
        ?.trim();

    return value || null;
}


function showUserAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "userAlert"
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