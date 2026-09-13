let doctorAppointments = [];

let currentDoctor = null;

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        try {

            currentDoctor =
                await loadCurrentUser();

            await loadDoctorAppointments();

            setupDoctorFilter();

        }
        catch (error) {

            console.error(error);

            showDoctorAlert(
                error.message ||
                "Không thể tải lịch khám.",
                "danger"
            );

        }

    }
);


async function loadDoctorAppointments() {

    const response =
        await apiFetch(
            `/api/appointment/doctor/${currentDoctor.user_id}`
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


    doctorAppointments =
        Array.isArray(data)
            ? data
            : data.items || [];


    const today =
        getLocalDateString();


    const todayAppointments =
        doctorAppointments.filter(
            appointment =>
                appointment
                    .appointment_time
                    .startsWith(today)
        );


    renderSummary(
        todayAppointments
    );


    renderDoctorAppointments(
        todayAppointments
    );


    renderUpcomingAppointments();


    renderRecentPatients();
}

function getLocalDateString() {

    const now =
        new Date();


    const year =
        now.getFullYear();


    const month =
        String(
            now.getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            now.getDate()
        ).padStart(
            2,
            "0"
        );


    return `${year}-${month}-${day}`;

}


function renderSummary(
    appointments
) {

    document.getElementById(
        "todayTotal"
    ).textContent =
        appointments.length;


    document.getElementById(
        "confirmedTotal"
    ).textContent =
        appointments.filter(
            appointment =>
                appointment.status ===
                "Confirmed"
        ).length;


    document.getElementById(
        "completedTotal"
    ).textContent =
        appointments.filter(
            appointment =>
                appointment.status ===
                "Completed"
        ).length;


    const now =
        new Date();


    const upcoming =
        doctorAppointments.filter(
            appointment => {

                const appointmentTime =
                    new Date(
                        appointment.appointment_time
                    );


                return (
                    appointmentTime > now &&
                    appointment.status ===
                    "Confirmed"
                );

            }
        );


    document.getElementById(
        "upcomingTotal"
    ).textContent =
        upcoming.length;
}

function renderDoctorAppointments(
    appointments
) {

    const filter =
        document.getElementById(
            "appointmentFilter"
        ).value;


    let filtered =
        appointments;


    if (filter !== "all") {

        filtered =
            appointments.filter(
                item =>
                    item.status === filter
            );

    }


    filtered.sort(
        (a, b) =>
            new Date(a.appointment_time) -
            new Date(b.appointment_time)
    );


    const tbody =
        document.getElementById(
            "doctorAppointmentList"
        );


    if (!filtered.length) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="text-center py-5 text-secondary">

                    Không có lịch phù hợp.

                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        filtered.map(
            appointment => {

                let action = "";


                if (
                    appointment.status ===
                    "Confirmed"
                ) {

                    action = `
                        <a
                            href="/doctor/examination/${appointment.appointment_id}"
                            class="btn btn-sm btn-primary">

                            <i class="bi bi-heart-pulse me-1"></i>

                            Khám bệnh

                        </a>
                    `;

                }
                else if (
                    appointment.status ===
                    "Completed"
                ) {

                    action = `
                        <a
                            href="/doctor/examination/${appointment.appointment_id}"
                            class="btn btn-sm btn-outline-primary">

                            <i class="bi bi-eye me-1"></i>

                            Xem hồ sơ

                        </a>
                    `;

                }
                else {

                    action = `
                        <span class="text-secondary">
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

                            <div class="fw-semibold">

                                ${escapeHtml(
                                    appointment.patient_name
                                )}

                            </div>

                            <div class="small text-secondary">

                                #${appointment.patient_id}

                            </div>

                        </td>


                        <td>

                            ${escapeHtml(
                                appointment.patient_phone ||
                                "Chưa cập nhật"
                            )}

                        </td>


                        <td>

                            ${escapeHtml(
                                appointment.specialty_name
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
        ).join("");

}


function setupDoctorFilter() {

    document
        .getElementById(
            "appointmentFilter"
        )
        .addEventListener(
            "change",
            async () => {

                const today =
                    getLocalDateString();


                renderDoctorAppointments(
                    doctorAppointments.filter(
                        appointment =>
                            appointment
                                .appointment_time
                                .startsWith(today)
                    )
                );

            }
        );

}


function showDoctorAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "doctorAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}

function renderUpcomingAppointments() {

    const container =
        document.getElementById(
            "upcomingAppointments"
        );


    const now =
        new Date();


    const upcoming =
        [...doctorAppointments]
            .filter(
                appointment => {

                    const appointmentTime =
                        new Date(
                            appointment.appointment_time
                        );


                    return (
                        appointmentTime > now &&
                        appointment.status ===
                        "Confirmed"
                    );

                }
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


    if (!upcoming.length) {

        container.innerHTML = `
            <div
                class="text-secondary small py-2">

                Không có lịch khám sắp tới.

            </div>
        `;

        return;

    }


    container.innerHTML =
        upcoming.map(
            appointment => {

                return `
                    <div
                        class="d-flex
                               justify-content-between
                               align-items-center
                               gap-3
                               border-bottom
                               py-3">

                        <div>

                            <div
                                class="fw-semibold">

                                ${escapeHtml(
                                    appointment.patient_name
                                )}

                            </div>

                            <div
                                class="small text-secondary">

                                ${formatDateTime(
                                    appointment.appointment_time
                                )}

                            </div>

                            <div
                                class="small text-secondary">

                                ${escapeHtml(
                                    appointment.specialty_name ||
                                    ""
                                )}

                            </div>

                        </div>


                        <a
                            href="/doctor/examination/${appointment.appointment_id}"
                            class="btn
                                   btn-sm
                                   btn-outline-primary">

                            Xem

                        </a>

                    </div>
                `;

            }
        ).join("");
}

function renderRecentPatients() {

    const container =
        document.getElementById(
            "recentPatients"
        );


    const recent =
        [...doctorAppointments]
            .filter(
                appointment =>
                    appointment.patient_id
            )
            .sort(
                (a, b) => {

                    const timeDiff =
                        new Date(
                            b.appointment_time
                        ) -
                        new Date(
                            a.appointment_time
                        );


                    if (
                        timeDiff !== 0
                    ) {

                        return timeDiff;

                    }


                    return (
                        a.status ===
                        "Completed"
                    ) ? -1 : 1;

                }
            )
            .slice(0, 5);


    if (!recent.length) {

        container.innerHTML = `
            <div
                class="text-secondary small">

                Chưa có dữ liệu bệnh nhân.

            </div>
        `;

        return;

    }


    container.innerHTML =
        recent.map(
            appointment => {

                return `
                    <div
                        class="border-bottom py-3">

                        <div
                            class="d-flex
                                   justify-content-between
                                   align-items-start
                                   gap-3">

                            <div>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        appointment.patient_name
                                    )}

                                </div>

                                <div
                                    class="small text-secondary">

                                    Mã BN:
                                    #${appointment.patient_id}

                                </div>

                            </div>


                            <div
                                class="text-end">

                                ${renderStatusBadge(
                                    appointment.status
                                )}

                            </div>

                        </div>


                        <div
                            class="small text-secondary mt-2">

                            ${formatDateTime(
                                appointment.appointment_time
                            )}

                        </div>

                    </div>
                `;

            }
        ).join("");
}