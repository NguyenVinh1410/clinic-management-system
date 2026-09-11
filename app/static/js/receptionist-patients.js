let allPatients = [];


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

        }
        catch (error) {

            console.error(error);

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
            "Không thể tải danh sách bệnh nhân."
        );

    }


    allPatients =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderPatients(
        allPatients
    );

}

function renderPatients(
    patients
) {

    const tbody =
        document.getElementById(
            "patientList"
        );


    document.getElementById(
        "patientCount"
    ).textContent =
        `${patients.length} bệnh nhân`;


    if (!patients.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="6"
                    class="text-center py-5 text-secondary">

                    Không tìm thấy bệnh nhân.

                </td>

            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        patients
            .map(
                patient =>
                    `
                    <tr>

                        <td>

                            <div class="fw-semibold">

                                ${
                                    patient.full_name
                                }

                            </div>

                        </td>


                        <td>

                            <span class="text-secondary">

                                @${patient.username}

                            </span>

                        </td>


                        <td>

                            <div>
                                ${
                                    patient.phone ||
                                    "—"
                                }
                            </div>

                            <div class="small text-secondary">

                                ${
                                    patient.email ||
                                    "Chưa có email"
                                }

                            </div>

                        </td>


                        <td>

                            ${
                                patient.dob ||
                                "—"
                            }

                        </td>


                        <td>

                            <span
                                class="status-badge
                                ${
                                    patient.status ===
                                    "Active"
                                        ? "status-confirmed"
                                        : "status-cancelled"
                                }">

                                ${
                                    patient.status ===
                                    "Active"
                                        ? "Hoạt động"
                                        : "Đã khóa"
                                }

                            </span>

                        </td>


                        <td class="text-end">

                            <a
                                href="/receptionist/appointments?patient_id=${
                                    patient.user_id
                                }"
                                class="btn btn-sm btn-outline-primary">

                                <i class="bi bi-calendar2-week"></i>

                            </a>

                        </td>

                    </tr>
                    `
            )
            .join("");

}

function setupPatientSearch() {

    const input =
        document.getElementById(
            "patientSearch"
        );


    input.addEventListener(
        "input",
        () => {

            const keyword =
                input.value
                    .trim()
                    .toLowerCase();


            const filtered =
                allPatients.filter(
                    patient => {

                        return (

                            (
                                patient.full_name ||
                                ""
                            )
                                .toLowerCase()
                                .includes(keyword)

                            ||

                            (
                                patient.username ||
                                ""
                            )
                                .toLowerCase()
                                .includes(keyword)

                            ||

                            (
                                patient.email ||
                                ""
                            )
                                .toLowerCase()
                                .includes(keyword)

                            ||

                            (
                                patient.phone ||
                                ""
                            )
                                .includes(keyword)

                        );

                    }
                );


            renderPatients(
                filtered
            );

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