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

            await loadReceptionistDashboard();

        }
        catch (error) {

            console.error(error);

            showReceptionistAlert(
                error.message ||
                "Không thể tải dữ liệu dashboard.",
                "danger"
            );

        }

    }
);

async function loadReceptionistUser() {

    const response =
        await apiFetch(
            "/api/auth/me"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể lấy thông tin tài khoản."
        );

    }


    renderReceptionistHeader(
        data
    );

}

async function loadReceptionistDashboard() {

    const [
        patientsResponse,
        appointmentsResponse
    ] = await Promise.all([

        apiFetch(
            "/api/patient"
        ),

        apiFetch(
            "/api/appointment"
        ),

    ]);


    const patients =
        await parseApiResponse(
            patientsResponse
        );


    const appointments =
        await parseApiResponse(
            appointmentsResponse
        );


    if (!patientsResponse.ok) {

        throw new Error(
            patients.detail ||
            "Không thể tải danh sách bệnh nhân."
        );

    }


    if (!appointmentsResponse.ok) {

        throw new Error(
            appointments.detail ||
            "Không thể tải danh sách lịch khám."
        );

    }


    renderDashboardSummary(
        patients,
        appointments
    );

}

function renderDashboardSummary(
    patients,
    appointments
) {

    const today =
        new Date();


    const todayString =
        today.toISOString()
            .split("T")[0];


    const todayAppointments =
        appointments.filter(
            appointment =>
                appointment.appointment_time
                    .startsWith(todayString)
        );


    const pendingCheckins =
        todayAppointments.filter(
            appointment =>
                appointment.status ===
                "Pending"
        );


    document.getElementById(
        "totalPatients"
    ).textContent =
        patients.length;


    document.getElementById(
        "todayAppointments"
    ).textContent =
        todayAppointments.length;


    document.getElementById(
        "pendingCheckins"
    ).textContent =
        pendingCheckins.length;


    renderTodayAppointments(
        todayAppointments
    );

}

function renderTodayAppointments(
    appointments
) {

    const tbody =
        document.getElementById(
            "todayAppointmentList"
        );


    if (!appointments.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="text-center py-5 text-secondary">

                    Hôm nay chưa có lịch khám.

                </td>
            </tr>
        `;

        return;
    }


    appointments.sort(
        (a, b) =>
            new Date(
                a.appointment_time
            ) -
            new Date(
                b.appointment_time
            )
    );


    tbody.innerHTML =
        appointments
            .slice(0, 10)
            .map(
                appointment =>
                    `
                    <tr>

                        <td>
                            ${formatDateTime(
                                appointment
                                    .appointment_time
                            )}
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

                            <div class="small text-secondary">

                                ${
                                    appointment.specialty_name
                                }

                            </div>

                        </td>


                        <td>

                            ${renderStatusBadge(
                                appointment.status
                            )}

                        </td>


                        <td class="text-end">

                            <a
                                href="/receptionist/appointments"
                                class="btn btn-sm btn-outline-primary">

                                Xem

                            </a>

                        </td>

                    </tr>
                    `
            )
            .join("");

}

//function renderStatusBadge(
//    status
//) {
//
//    const config = {
//
//        Pending: {
//            text: "Chờ xác nhận",
//            className:
//                "status-pending",
//            icon: "bi-clock",
//        },
//
//        Confirmed: {
//            text: "Đã xác nhận",
//            className:
//                "status-confirmed",
//            icon:
//                "bi-check-circle",
//        },
//
//        Completed: {
//            text: "Đã hoàn thành",
//            className:
//                "status-completed",
//            icon:
//                "bi-check2-all",
//        },
//
//        Cancelled: {
//            text: "Đã hủy",
//            className:
//                "status-cancelled",
//            icon:
//                "bi-x-circle",
//        },
//
//    };
//
//
//    const item =
//        config[status] || {
//
//            text: status,
//
//            className: "",
//
//            icon:
//                "bi-info-circle",
//
//        };
//
//
//    return `
//        <span
//            class="status-badge ${item.className}">
//
//            <i
//                class="bi ${item.icon}">
//            </i>
//
//            ${item.text}
//
//        </span>
//    `;
//
//}

function showReceptionistAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "receptionistAlert"
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