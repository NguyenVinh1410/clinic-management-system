let patients = [];


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

            await loadPatients();

            setupPatientSearch();

            setupPatientRefresh();

        }
        catch (error) {

            console.error(
                error
            );

            showPatientAlert(
                error.message ||
                "Không thể tải danh sách bệnh nhân.",
                "danger"
            );

        }

    }
);


async function loadPatients() {

    const response =
        await apiFetch(
            "/api/patient"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải bệnh nhân."
        );

    }


    patients =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderPatients(
        patients
    );

}


function renderPatients(
    items
) {

    const tbody =
        document.getElementById(
            "patientList"
        );


    if (!items.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="6"
                    class="text-center
                           py-5
                           text-secondary">

                    Không tìm thấy bệnh nhân.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        items
            .map(
                patient => {

                    const status =
                        patient.status ===
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


                    return `
                        <tr>

                            <td>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        patient.full_name
                                    )}

                                </div>

                            </td>


                            <td>

                                ${escapeHtml(
                                    patient.username
                                )}

                            </td>


                            <td>

                                ${
                                    escapeHtml(
                                        patient.phone ||
                                        "Chưa cập nhật"
                                    )
                                }

                            </td>


                            <td>

                                ${
                                    escapeHtml(
                                        patient.email ||
                                        "Chưa cập nhật"
                                    )
                                }

                            </td>


                            <td>

                                ${
                                    patient.dob
                                        ? formatDateTime(
                                            patient.dob
                                          ).split(",")[0]
                                        : "Chưa cập nhật"
                                }

                            </td>


                            <td>

                                ${status}

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");

}


function setupPatientSearch() {

    const input =
        document.getElementById(
            "patientSearch"
        );


    input?.addEventListener(
        "input",
        () => {

            const keyword =
                input.value
                    .trim()
                    .toLowerCase();


            const filtered =
                patients.filter(
                    patient => {

                        const name =
                            String(
                                patient.full_name ||
                                ""
                            )
                            .toLowerCase();


                        const username =
                            String(
                                patient.username ||
                                ""
                            )
                            .toLowerCase();


                        const phone =
                            String(
                                patient.phone ||
                                ""
                            )
                            .toLowerCase();


                        return (
                            name.includes(
                                keyword
                            ) ||
                            username.includes(
                                keyword
                            ) ||
                            phone.includes(
                                keyword
                            )
                        );

                    }
                );


            renderPatients(
                filtered
            );

        }
    );

}


function setupPatientRefresh() {

    document
        .getElementById(
            "refreshPatients"
        )
        ?.addEventListener(
            "click",
            async () => {

                try {

                    await loadPatients();

                }
                catch (error) {

                    showPatientAlert(
                        error.message,
                        "danger"
                    );

                }

            }
        );

}


function showPatientAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "patientAlert"
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

}