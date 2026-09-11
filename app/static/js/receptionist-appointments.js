let allAppointments = [];


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

            await loadAppointments();

            setupAppointmentFilters();

        }
        catch (error) {

            console.error(
                error
            );

            showAppointmentAlert(
                error.message ||
                "Không thể tải lịch khám.",
                "danger"
            );

        }

    }
);

async function loadAppointments() {

    const response =
        await apiFetch(
            "/api/appointment"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải lịch khám."
        );

    }


    allAppointments =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderAppointments(
        allAppointments
    );

}

function renderAppointments(
    appointments
) {

    const tbody =
        document.getElementById(
            "appointmentList"
        );


    if (!appointments.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="6"
                    class="text-center py-5 text-secondary">

                    Không có lịch khám.

                </td>

            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        appointments
            .map(
                appointment =>
                    `
                    <tr>

                        <td>

                            <div class="fw-semibold">

                                ${
                                    formatDateTime(
                                        appointment
                                            .appointment_time
                                    )
                                }

                            </div>

                        </td>


                        <td>

                            <div class="fw-semibold">

                                Bệnh nhân #${
                                    appointment.patient_id
                                }

                            </div>

                        </td>


                        <td>

                            <div class="fw-semibold">

                                BS.
                                ${
                                    appointment.doctor_name
                                }

                            </div>

                        </td>


                        <td>

                            <span
                                class="text-secondary">

                                ${
                                    appointment
                                        .specialty_name
                                }

                            </span>

                        </td>


                        <td>

                            ${
                                renderStatusBadge(
                                    appointment.status
                                )
                            }

                        </td>

                        <td class="text-end">

                            ${
                                appointment.status === "Pending"
                                    ? `
                                        <button
                                            type="button"
                                            class="btn btn-sm btn-success me-1"
                                            onclick="confirmAppointment(
                                                ${appointment.appointment_id}
                                            )">

                                            <i class="bi bi-check-lg"></i>

                                        </button>
                                    `
                                    : ""
                            }


                            ${
                                appointment.status === "Pending" ||
                                appointment.status === "Confirmed"
                                ? `
                                    <button
                                        type="button"
                                        class="btn btn-sm btn-outline-danger"
                                        onclick="cancelAppointment(
                                        ${appointment.appointment_id}
                                        )">

                                        <i class="bi bi-x-lg"></i>

                                    </button>
                                `
                                : ""
                            }

                        </td>

                    </tr>
                    `
            )
            .join("");

}

function setupAppointmentFilters() {

    const dateInput =
        document.getElementById(
            "appointmentDate"
        );


    const statusSelect =
        document.getElementById(
            "appointmentStatus"
        );


    const searchInput =
        document.getElementById(
            "appointmentSearch"
        );


    const applyFilters = () => {

        const date =
            dateInput.value;


        const status =
            statusSelect.value;


        const keyword =
            searchInput.value
                .trim()
                .toLowerCase();


        const filtered =
            allAppointments.filter(
                appointment => {

                    const appointmentDate =
                        appointment
                            .appointment_time
                            .split("T")[0];


                    const matchesDate =
                        !date ||
                        appointmentDate === date;


                    const matchesStatus =
                        !status ||
                        appointment.status ===
                        status;


                    const doctorName =
                        (
                            appointment
                                .doctor_name ||
                            ""
                        ).toLowerCase();


                    const matchesSearch =
                        !keyword ||
                        doctorName.includes(
                            keyword
                        ) ||
                        String(
                            appointment.patient_id
                        ).includes(
                            keyword
                        );


                    return (
                        matchesDate &&
                        matchesStatus &&
                        matchesSearch
                    );

                }
            );


        renderAppointments(
            filtered
        );

    };


    dateInput.addEventListener(
        "change",
        applyFilters
    );


    statusSelect.addEventListener(
        "change",
        applyFilters
    );


    searchInput.addEventListener(
        "input",
        applyFilters
    );

}

function showAppointmentAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "appointmentAlert"
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

function openAppointment(
    appointmentId
) {

    window.location.href =
        `/receptionist/appointments?appointment_id=${appointmentId}`;

}

async function confirmAppointment(
    appointmentId
) {

    if (
        !confirm(
            "Bạn có chắc muốn xác nhận lịch khám này?"
        )
    ) {
        return;
    }


    try {

        const response =
            await apiFetch(
                `/api/appointment/${appointmentId}/status`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        status: "Confirmed"
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
                "Không thể xác nhận lịch khám."
            );

        }


        showAppointmentAlert(
            "Đã xác nhận lịch khám.",
            "success"
        );


        await loadAppointments();

    }
    catch (error) {

        console.error(
            error
        );


        showAppointmentAlert(
            error.message ||
            "Xác nhận lịch khám thất bại.",
            "danger"
        );

    }

}

async function cancelAppointment(
    appointmentId
) {

    if (
        !confirm(
            "Bạn có chắc muốn hủy lịch khám này?"
        )
    ) {
        return;
    }


    try {

        const response =
            await apiFetch(
                `/api/appointment/${appointmentId}/status`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        status: "Cancelled"
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
                "Không thể hủy lịch khám."
            );

        }


        showAppointmentAlert(
            "Đã hủy lịch khám.",
            "success"
        );


        await loadAppointments();

    }
    catch (error) {

        console.error(
            error
        );


        showAppointmentAlert(
            error.message ||
            "Hủy lịch khám thất bại.",
            "danger"
        );

    }

}