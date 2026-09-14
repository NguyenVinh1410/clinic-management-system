let appointments = [];


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

            setupAppointmentRefresh();

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


    appointments =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderAppointments(
        appointments
    );

}


function renderAppointments(
    items
) {

    const tbody =
        document.getElementById(
            "appointmentList"
        );


    if (!items.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="6"
                    class="text-center
                           py-5
                           text-secondary">

                    Không có lịch khám phù hợp.

                </td>

            </tr>
        `;

        return;

    }


    const sorted =
        [...items].sort(
            (a, b) =>
                new Date(
                    a.appointment_time
                ) -
                new Date(
                    b.appointment_time
                )
        );


    tbody.innerHTML =
        sorted
            .map(
                appointment => {

                    let action = "";


                    if (
                        appointment.status ===
                        "Pending"
                    ) {

                        action = `
                            <button
                                type="button"
                                class="btn
                                       btn-sm
                                       btn-primary"
                                data-checkin="${appointment.appointment_id}">

                                <i
                                    class="bi bi-person-check me-1">
                                </i>

                                Tiếp nhận

                            </button>
                        `;

                    }
                    else if (
                        appointment.status ===
                        "Confirmed"
                    ) {

                        action = `
                            <button
                                type="button"
                                class="btn
                                       btn-sm
                                       btn-outline-danger"
                                data-cancel="${appointment.appointment_id}">

                                Hủy

                            </button>
                        `;

                    }
                    else {

                        action = `
                            <span
                                class="text-secondary small">

                                Không có thao tác

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

                                    ${escapeHtml(
                                        appointment.patient_name
                                    )}

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

                                ${escapeHtml(
                                    appointment.doctor_name
                                )}

                            </td>


                            <td>

                                ${escapeHtml(
                                    appointment.specialty_name ||
                                    "Chưa cập nhật"
                                )}

                            </td>


                            <td>

                                ${renderStatusBadge(
                                    appointment.status
                                )}

                            </td>


                            <td class="text-end">

                                ${action}

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");


    bindAppointmentActions();

}


function bindAppointmentActions() {

    document
        .querySelectorAll(
            "[data-checkin]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        checkinAppointment(
                            Number(
                                button.dataset.checkin
                            )
                        )
                );

            }
        );


    document
        .querySelectorAll(
            "[data-cancel]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () =>
                        cancelAppointment(
                            Number(
                                button.dataset.cancel
                            )
                        )
                );

            }
        );

}


async function checkinAppointment(
    appointmentId
) {

    const confirmed =
        window.confirm(
            "Xác nhận tiếp nhận bệnh nhân?"
        );


    if (!confirmed) {

        return;

    }


    const response =
        await apiFetch(
            `/api/appointment/${appointmentId}/checkin`,
            {
                method: "POST",
            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tiếp nhận."
        );

    }


    showAppointmentAlert(
        "Đã tiếp nhận bệnh nhân.",
        "success"
    );


    await loadAppointments();

}


async function cancelAppointment(
    appointmentId
) {

    const confirmed =
        window.confirm(
            "Bạn có chắc muốn hủy lịch khám này?"
        );


    if (!confirmed) {

        return;

    }


    const response =
        await apiFetch(
            `/api/appointment/${appointmentId}/cancel`,
            {
                method: "POST",
            }
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể hủy lịch."
        );

    }


    showAppointmentAlert(
        "Đã hủy lịch khám.",
        "success"
    );


    await loadAppointments();

}


function setupAppointmentFilters() {

    const search =
        document.getElementById(
            "appointmentSearch"
        );


    const status =
        document.getElementById(
            "appointmentStatus"
        );


    const date =
        document.getElementById(
            "appointmentDate"
        );


    function applyFilters() {

        const keyword =
            search.value
                .trim()
                .toLowerCase();


        const selectedStatus =
            status.value;


        const selectedDate =
            date.value;


        const filtered =
            appointments.filter(
                appointment => {

                    const patient =
                        String(
                            appointment.patient_name ||
                            ""
                        )
                        .toLowerCase();


                    const doctor =
                        String(
                            appointment.doctor_name ||
                            ""
                        )
                        .toLowerCase();


                    const appointmentDate =
                        String(
                            appointment.appointment_time ||
                            ""
                        ).slice(0, 10);


                    const matchSearch =
                        !keyword ||
                        patient.includes(
                            keyword
                        ) ||
                        doctor.includes(
                            keyword
                        );


                    const matchStatus =
                        !selectedStatus ||
                        appointment.status ===
                        selectedStatus;


                    const matchDate =
                        !selectedDate ||
                        appointmentDate ===
                        selectedDate;


                    return (
                        matchSearch &&
                        matchStatus &&
                        matchDate
                    );

                }
            );


        renderAppointments(
            filtered
        );

    }


    search.addEventListener(
        "input",
        applyFilters
    );


    status.addEventListener(
        "change",
        applyFilters
    );


    date.addEventListener(
        "change",
        applyFilters
    );

}


function setupAppointmentRefresh() {

    document
        .getElementById(
            "refreshAppointments"
        )
        ?.addEventListener(
            "click",
            loadAppointments
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