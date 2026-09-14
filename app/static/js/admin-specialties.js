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

            setupSpecialtyForm();

            setupRefresh();

        }
        catch (error) {

            console.error(
                error
            );

            showSpecialtyAlert(
                error.message ||
                "Không thể tải chuyên khoa.",
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


    renderSpecialties();

}


function renderSpecialties() {

    const tbody =
        document.getElementById(
            "specialtyList"
        );


    if (!specialties.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="3"
                    class="text-center
                           py-5
                           text-secondary">

                    Chưa có chuyên khoa.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        specialties
            .map(
                specialty => `
                    <tr>

                        <td class="fw-semibold">

                            ${escapeHtml(
                                specialty.name
                            )}

                        </td>


                        <td>

                            ${escapeHtml(
                                specialty.description ||
                                "Chưa cập nhật"
                            )}

                        </td>


                        <td
                            class="text-end">

                            <button
                                type="button"
                                class="btn
                                       btn-sm
                                       btn-outline-primary"
                                data-edit-specialty="${specialty.specialty_id}">

                                <i
                                    class="bi bi-pencil">
                                </i>

                            </button>

                            <button
                                type="button"
                                class="btn
                                       btn-sm
                                       btn-outline-danger"
                                data-delete-specialty="${specialty.specialty_id}">

                                <i
                                    class="bi bi-trash">
                                </i>

                            </button>

                        </td>

                    </tr>
                `
            )
            .join("");

    document
        .querySelectorAll(
            "[data-edit-specialty]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        editSpecialty(
                            Number(
                                button.dataset.editSpecialty
                            )
                        )
                );

            }
        );

    document
        .querySelectorAll(
            "[data-delete-specialty]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        deleteSpecialty(
                            Number(
                                button.dataset.deleteSpecialty
                            )
                        )
                );

            }
        );

}


function setupSpecialtyForm() {

    const form =
        document.getElementById(
            "specialtyForm"
        );


    form.addEventListener(
        "submit",
        createSpecialty
    );

}


async function createSpecialty(
    event
) {

    event.preventDefault();


    const name =
        document
            .getElementById(
                "specialtyName"
            )
            .value
            .trim();


    const description =
        document
            .getElementById(
                "specialtyDescription"
            )
            .value
            .trim();


    if (!name) {

        showSpecialtyAlert(
            "Vui lòng nhập tên chuyên khoa.",
            "danger"
        );

        return;

    }


    const response =
        await apiFetch(
            "/api/specialty",
            {

                method: "POST",

                body:
                    JSON.stringify({

                        name:
                            name,

                        description:
                            description ||
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
            "Không thể tạo chuyên khoa."
        );

    }


    event.target.reset();


    showSpecialtyAlert(
        "Đã thêm chuyên khoa.",
        "success"
    );


    await loadSpecialties();

}

async function editSpecialty(
    specialtyId
) {

    const specialty =
        specialties.find(
            item =>
                Number(
                    item.specialty_id
                ) ===
                Number(
                    specialtyId
                )
        );


    if (!specialty) {

        return;

    }


    const name =
        window.prompt(
            "Tên chuyên khoa:",
            specialty.name
        );


    if (name === null) {

        return;

    }


    const description =
        window.prompt(
            "Mô tả:",
            specialty.description || ""
        );


    if (description === null) {

        return;

    }


    const response =
        await apiFetch(
            `/api/specialty/${specialtyId}`,
            {

                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        name:
                            name.trim(),

                        description:
                            description.trim() ||
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
            "Không thể cập nhật chuyên khoa."
        );

    }


    showSpecialtyAlert(
        "Đã cập nhật chuyên khoa.",
        "success"
    );


    await loadSpecialties();

}

async function deleteSpecialty(
    specialtyId
) {

    const confirmed =
        window.confirm(
            "Bạn có chắc muốn xóa chuyên khoa này?"
        );


    if (!confirmed) {

        return;

    }


    const response =
        await apiFetch(
            `/api/specialty/${specialtyId}`,
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
            "Không thể xóa chuyên khoa."
        );

    }


    showSpecialtyAlert(
        "Đã xóa chuyên khoa.",
        "success"
    );


    await loadSpecialties();

}


function setupRefresh() {

    document
        .getElementById(
            "refreshSpecialties"
        )
        ?.addEventListener(
            "click",
            loadSpecialties
        );

}


function showSpecialtyAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "specialtyAlert"
        );


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