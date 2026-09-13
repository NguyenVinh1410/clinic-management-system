let patientAppointments = [];

let currentAppointmentFilter =
    "all";


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await loadHeader();

            await loadAppointments();

            setupFilters();

        }
        catch (error) {

            console.error(
                error
            );

        }

    }
);


async function loadHeader() {

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
            data.detail
        );

    }


    const name =
        data.full_name ||
        data.username;


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


async function loadAppointments() {

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
            data.detail
        );

    }


    patientAppointments =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderAppointments();

}


function setupFilters() {

    document
        .querySelectorAll(
            ".appointment-filter"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        document
                            .querySelectorAll(
                                ".appointment-filter"
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "active",
                                        "btn-primary"
                                    )
                            );


                        document
                            .querySelectorAll(
                                ".appointment-filter"
                            )
                            .forEach(
                                item => {

                                    if (
                                        item
                                            .dataset
                                            .filter ===
                                        button
                                            .dataset
                                            .filter
                                    ) {

                                        item.classList.add(
                                            "active",
                                            "btn-primary"
                                        );

                                        item.classList.remove(
                                            "btn-outline-primary"
                                        );

                                    }
                                    else {

                                        item.classList.add(
                                            "btn-outline-primary"
                                        );

                                        item.classList.remove(
                                            "btn-primary"
                                        );

                                    }

                                }
                            );


                        currentAppointmentFilter =
                            button.dataset.filter;


                        renderAppointments();

                    }
                );

            }
        );

}


function renderAppointments() {

    const container =
        document.getElementById(
            "appointmentList"
        );


    let appointments =
        [...patientAppointments];


    if (
        currentAppointmentFilter !==
        "all"
    ) {

        if (
            currentAppointmentFilter ===
            "upcoming"
        ) {

            const now =
                new Date();


            appointments =
                appointments.filter(
                    appointment =>
                        new Date(
                            appointment.appointment_time
                        ) >= now &&
                        appointment.status !==
                        "Completed" &&
                        appointment.status !==
                        "Cancelled"
                );

        }
        else {

            appointments =
                appointments.filter(
                    appointment =>
                        appointment.status ===
                        currentAppointmentFilter
                );

        }

    }


    appointments.sort(
        (a, b) =>
            new Date(
                b.appointment_time
            ) -
            new Date(
                a.appointment_time
            )
    );


    if (
        appointments.length === 0
    ) {

        container.innerHTML = `
            <div class="text-center py-5 text-secondary">

                <i class="bi bi-calendar-x fs-1 d-block mb-3"></i>

                Không có lịch khám phù hợp.

            </div>
        `;

        return;

    }


    container.innerHTML =
        appointments
            .map(
                appointment =>
                    renderAppointmentCard(
                        appointment
                    )
            )
            .join("");


    container
        .querySelectorAll(
            "[data-cancel-id]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        cancelAppointment(
                            Number(
                                button.dataset.cancelId
                            )
                        );

                    }
                );

            }
        );

}


function renderAppointmentCard(
    appointment
) {

    const canCancel =
        appointment.status ===
        "Pending" ||
        appointment.status ===
        "Confirmed";


    return `

        <div
            class="appointment-card mb-3">

            <div
                class="d-flex flex-column flex-lg-row justify-content-between gap-3">

                <div>

                    <div class="d-flex align-items-center gap-2 mb-2">

                        <i
                            class="bi bi-calendar-event text-primary">
                        </i>

                        <span
                            class="fw-semibold">

                            ${formatDateTime(
                                appointment.appointment_time
                            )}

                        </span>

                    </div>

                    <div class="mb-2">

                        <div class="fw-semibold">
                            BS. ${appointment.doctor_name}
                        </div>

                        <div class="small text-secondary">
                            ${appointment.specialty_name}
                        </div>

                    </div>

                    <div
                        class="small text-secondary">

                        Mã lịch:
                        #${appointment.appointment_id}

                    </div>


                    <div
                        class="small text-secondary">

                        Mã ca:
                        #${appointment.schedule_id}

                    </div>

                </div>


                <div
                    class="d-flex flex-wrap align-items-center gap-2">

                    ${renderStatusBadge(
                        appointment.status
                    )}


                    ${
                        canCancel
                            ? `
                                <button
                                    type="button"
                                    class="btn btn-sm btn-outline-danger"
                                    data-cancel-id="${appointment.appointment_id}">

                                    Hủy lịch

                                </button>
                              `
                            : ""
                    }

                </div>

            </div>

        </div>

    `;

}


async function cancelAppointment(
    appointmentId
) {

    const confirmed =
        window.confirm(
            "Bạn có chắc muốn hủy lịch khám này không?"
        );


    if (!confirmed) {

        return;

    }


    try {

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

            showAppointmentAlert(
                typeof data === "object"
                    ? data.detail ||
                      "Không thể hủy lịch."
                    : "Không thể hủy lịch.",
                "danger"
            );

            return;

        }


        showAppointmentAlert(
            "Hủy lịch thành công.",
            "success"
        );


        await loadAppointments();

    }
    catch (error) {

        console.error(
            error
        );


        showAppointmentAlert(
            "Không thể kết nối tới máy chủ.",
            "danger"
        );

    }

}

function showAppointmentAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "appointmentAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}