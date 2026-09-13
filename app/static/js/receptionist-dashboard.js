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
        appointmentsResponse,
        invoicesResponse
    ] =
        await Promise.all([

            apiFetch(
                "/api/patient"
            ),

            apiFetch(
                "/api/appointment"
            ),

            apiFetch(
                "/api/invoice"
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


    const invoices =
        await parseApiResponse(
            invoicesResponse
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


    if (!invoicesResponse.ok) {

        throw new Error(
            invoices.detail ||
            "Không thể tải danh sách hóa đơn."
        );

    }


    renderDashboardSummary(
        patients,
        appointments,
        invoices
    );

}

function renderDashboardSummary(
    patients,
    appointments,
    invoices
) {

    const today =
        new Date();


    const year =
        today.getFullYear();


    const month =
        String(
            today.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            today.getDate()
        ).padStart(
            2,
            "0"
        );


    const todayString =
        `${year}-${month}-${day}`;


    const todayAppointments =
        appointments.filter(
            appointment =>
                appointment
                    .appointment_time
                    .startsWith(
                        todayString
                    )
        );


    const pendingCheckins =
        todayAppointments.filter(
            appointment =>
                appointment.status ===
                "Pending"
        );


    const confirmedAppointments =
        todayAppointments.filter(
            appointment =>
                appointment.status ===
                "Confirmed"
        );


    const unpaidInvoices =
        invoices.filter(
            invoice =>
                invoice.status ===
                "Unpaid"
        );


    const todayPaidInvoices =
        invoices.filter(
            invoice => {

                if (
                    invoice.status !==
                    "Paid"
                ) {

                    return false;

                }


                if (
                    !invoice.paid_at
                ) {

                    return false;

                }


                return invoice.paid_at
                    .startsWith(
                        todayString
                    );

            }
        );


    const todayRevenue =
        todayPaidInvoices.reduce(
            (
                total,
                invoice
            ) => {

                return (
                    total +
                    Number(
                        invoice.total_amount ||
                        0
                    )
                );

            },
            0
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


    document.getElementById(
        "confirmedAppointments"
    ).textContent =
        confirmedAppointments.length;


    document.getElementById(
        "unpaidInvoices"
    ).textContent =
        unpaidInvoices.length;


    document.getElementById(
        "todayRevenue"
    ).textContent =
        formatCurrency(
            todayRevenue
        );


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
                    class="text-center
                           py-5
                           text-secondary">

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
                appointment => {

                    let action = "";


                    if (
                        appointment.status ===
                        "Pending"
                    ) {

                        action = `
                            <a
                                href="/receptionist/checkin"
                                class="btn
                                       btn-sm
                                       btn-primary">

                                <i
                                    class="bi bi-person-check me-1">
                                </i>

                                Tiếp nhận

                            </a>
                        `;

                    }

                    else if (
                        appointment.status ===
                        "Confirmed"
                    ) {

                        action = `
                            <a
                                href="/receptionist/appointments"
                                class="btn
                                       btn-sm
                                       btn-outline-primary">

                                <i
                                    class="bi bi-eye me-1">
                                </i>

                                Xem

                            </a>
                        `;

                    }

                    else if (
                        appointment.status ===
                        "Completed"
                    ) {

                        action = `
                            <a
                                href="/receptionist/appointments"
                                class="btn
                                       btn-sm
                                       btn-outline-secondary">

                                <i
                                    class="bi bi-eye me-1">
                                </i>

                                Xem

                            </a>
                        `;

                    }

                    else if (
                        appointment.status ===
                        "Cancelled"
                    ) {

                        action = `
                            <span
                                class="text-secondary">

                                —

                            </span>
                        `;

                    }


                    return `
                        <tr>

                            <td>
                                ${formatDateTime(
                                    appointment.appointment_time
                                )}
                            </td>


                            <td>

                                <div
                                    class="fw-semibold">

                                    ${
                                        appointment.patient_name ||
                                        "Bệnh nhân #" +
                                        appointment.patient_id
                                    }

                                </div>

                                <div
                                    class="small
                                           text-secondary">

                                    ${
                                        appointment.patient_phone ||
                                        "Chưa có SĐT"
                                    }

                                </div>

                            </td>


                            <td>

                                <div
                                    class="fw-semibold">

                                    BS.
                                    ${escapeHtml(
                                        appointment.doctor_name ||
                                        ""
                                    )}

                                </div>

                                <div
                                    class="small
                                           text-secondary">

                                    ${escapeHtml(
                                        appointment.specialty_name ||
                                        "Chưa cập nhật"
                                    )}

                                </div>

                            </td>


                            <td>

                                ${renderStatusBadge(
                                    appointment.status
                                )}

                            </td>


                            <td
                                class="text-end">

                                ${action}

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");

}

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