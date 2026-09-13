document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            const user =
                await loadPatientUser();

            setupPatientHeader(
                user
            );

            await Promise.all([
                loadUpcomingAppointments(),
                loadRecentInvoices(),
            ]);

        }
        catch (error) {

            console.error(
                error
            );

            showPatientAlert(
                "Không thể tải dữ liệu bệnh nhân.",
                "danger"
            );

        }

    }
);


async function loadPatientUser() {

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
            "Không thể tải hồ sơ"
        );

    }


    return data;

}


function setupPatientHeader(
    patient
) {

    const name =
        patient.full_name ||
        patient.username ||
        "Bệnh nhân";


    document.getElementById(
        "patientWelcome"
    ).textContent =
        name;


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


async function loadUpcomingAppointments() {

    const response =
        await apiFetch(
            "/api/appointment/my"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải lịch khám"
        );

    }


    const appointments =
        Array.isArray(data)
            ? data
            : data.items || [];


    const upcoming =
        appointments
            .filter(
                item =>
                    item.status !==
                    "Completed" &&
                    item.status !==
                    "Cancelled"
            )
            .sort(
                (a, b) =>
                    new Date(
                        a.appointment_time
                    ) -
                    new Date(
                        b.appointment_time
                    )
            )
            .slice(0, 5);


    renderUpcomingAppointments(
        upcoming
    );

}


function renderUpcomingAppointments(
    appointments
) {

    const tbody =
        document.getElementById(
            "upcomingAppointments"
        );


    if (
        !appointments ||
        appointments.length === 0
    ) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="4"
                    class="text-center py-5">

                    <div class="text-secondary mb-2">

                        <i class="bi bi-calendar-x fs-2"></i>

                    </div>

                    <div class="fw-semibold">
                        Chưa có lịch khám sắp tới
                    </div>

                    <a
                        href="/patient/book-appointment"
                        class="btn btn-sm btn-primary mt-3">

                        Đặt lịch ngay

                    </a>

                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        appointments
            .map(
                appointment => `

                    <tr>

                        <td>

                            <div
                                class="fw-semibold">

                                ${formatDateTime(
                                    appointment.appointment_time
                                )}

                            </div>

                        </td>


                        <td>

                            <div class="fw-semibold">
                                BS. ${appointment.doctor_name}
                            </div>

                            <div class="small text-secondary">
                                ${appointment.specialty_name}
                            </div>

                        </td>


                        <td>

                            ${renderStatusBadge(
                                appointment.status
                            )}

                        </td>


                        <td
                            class="text-end">

                            <a
                                href="/patient/appointments"
                                class="btn btn-sm btn-light">

                                Xem

                            </a>

                        </td>

                    </tr>

                `
            )
            .join("");

}


async function loadRecentInvoices() {

    const response =
        await apiFetch(
            "/api/invoice/my"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải hóa đơn"
        );

    }


    const invoices =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderRecentInvoices(
        invoices.slice(0, 4)
    );

}


function renderRecentInvoices(
    invoices
) {

    const container =
        document.getElementById(
            "recentInvoices"
        );


    if (
        !invoices ||
        invoices.length === 0
    ) {

        container.innerHTML = `
            <div class="text-center py-4 text-secondary">

                <i class="bi bi-receipt-cutoff fs-2 d-block mb-2"></i>

                Chưa có hóa đơn.

            </div>
        `;

        return;

    }


    container.innerHTML =
        invoices
            .map(
                invoice => `

                    <div
                        class="invoice-item">

                        <div>

                            <div class="fw-semibold">

                                Hóa đơn #${invoice.invoice_id}

                            </div>


                            <div
                                class="small text-secondary">

                                Lịch khám #${invoice.appointment_id}

                            </div>

                        </div>


                        <div
                            class="text-end">

                            <div class="fw-bold">

                                ${formatCurrency(
                                    invoice.total_amount
                                )}

                            </div>


                            <div class="small mt-1">

                                ${renderInvoiceStatus(
                                    invoice.status
                                )}

                            </div>

                        </div>

                    </div>

                `
            )
            .join("");

}

function renderInvoiceStatus(
    status
) {

    if (status === "Paid") {

        return `
            <span
                class="badge text-bg-success">
                Đã thanh toán
            </span>
        `;

    }


    return `
        <span
            class="badge text-bg-warning">
            Chưa thanh toán
        </span>
    `;

}

function showPatientAlert(
    message,
    type = "danger"
) {

    const alertBox =
        document.getElementById(
            "patientAlert"
        );


    alertBox.className =
        `alert alert-${type}`;


    alertBox.textContent =
        message;


    alertBox.classList.remove(
        "d-none"
    );

}