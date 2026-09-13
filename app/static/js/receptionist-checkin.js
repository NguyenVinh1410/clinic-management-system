let allCheckinAppointments = [];

let patientMap = {};


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

            await loadCheckinData();

            setupCheckinFilters();

        }
        catch (error) {

            console.error(error);

            showCheckinAlert(
                error.message ||
                "Không thể tải dữ liệu tiếp nhận.",
                "danger"
            );

        }

    }
);


async function loadCheckinData() {

    const [
        appointmentsResponse,
        patientsResponse,
    ] = await Promise.all([

        apiFetch(
            "/api/appointment"
        ),

        apiFetch(
            "/api/patient"
        ),

    ]);


    const appointments =
        await parseApiResponse(
            appointmentsResponse
        );


    const patients =
        await parseApiResponse(
            patientsResponse
        );


    if (!appointmentsResponse.ok) {

        throw new Error(
            appointments.detail ||
            "Không thể tải lịch khám."
        );

    }


    if (!patientsResponse.ok) {

        throw new Error(
            patients.detail ||
            "Không thể tải danh sách bệnh nhân."
        );

    }


    patientMap = {};

    patients.forEach(
        patient => {

            patientMap[
                patient.user_id
            ] = patient;

        }
    );


    const today =
        getLocalDateString();


    allCheckinAppointments =
        appointments.filter(
            appointment =>
                appointment
                    .appointment_time
                    .startsWith(today)
        );


    renderCheckinSummary(
        allCheckinAppointments
    );


    renderCheckinAppointments(
        allCheckinAppointments
    );

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


function renderCheckinSummary(
    appointments
) {

    const total =
        appointments.length;


    const pending =
        appointments.filter(
            appointment =>
                appointment.status ===
                "Pending"
        ).length;


    const confirmed =
        appointments.filter(
            appointment =>
                appointment.status ===
                "Confirmed"
        ).length;


    const cancelled =
        appointments.filter(
            appointment =>
                appointment.status ===
                "Cancelled"
        ).length;


    document.getElementById(
        "todayTotal"
    ).textContent =
        total;


    document.getElementById(
        "pendingCount"
    ).textContent =
        pending;


    document.getElementById(
        "checkedInCount"
    ).textContent =
        confirmed;


    document.getElementById(
        "cancelledCount"
    ).textContent =
        cancelled;

}


function renderCheckinAppointments(
    appointments
) {

    const tbody =
        document.getElementById(
            "checkinList"
        );


    if (!appointments.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="7"
                    class="text-center py-5 text-secondary">

                    Hôm nay chưa có lịch khám.

                </td>

            </tr>
        `;

        return;

    }


    const filtered =
        applyCheckinSearch(
            appointments
        );


    if (!filtered.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="7"
                    class="text-center py-5 text-secondary">

                    Không tìm thấy lịch phù hợp.

                </td>

            </tr>
        `;

        return;

    }


    filtered.sort(
        (a, b) =>
            new Date(
                a.appointment_time
            ) -
            new Date(
                b.appointment_time
            )
    );


    tbody.innerHTML =
        filtered
            .map(
                appointment =>
                    renderCheckinRow(
                        appointment
                    )
            )
            .join("");

}


function renderCheckinRow(
    appointment
) {

    const patient =
        patientMap[
            appointment.patient_id
        ];


    const patientName =
        patient?.full_name ||
        `Bệnh nhân #${appointment.patient_id}`;


    const patientPhone =
        patient?.phone ||
        "Chưa cập nhật";


    let actionHtml = "";


    if (
        appointment.status ===
        "Pending"
    ) {

        actionHtml = `
            <button
                type="button"
                class="btn btn-sm btn-primary"
                onclick="checkInAppointment(
                    ${appointment.appointment_id}
                )">

                <i class="bi bi-person-check me-1"></i>

                Tiếp nhận

            </button>
        `;

    }
    else if (
        appointment.status ===
        "Confirmed"
    ) {

        actionHtml = `
            <span
                class="badge text-bg-success">

                <i class="bi bi-check-circle me-1"></i>

                Đã tiếp nhận

            </span>
        `;

    }
    else {

        actionHtml =
            renderStatusBadge(
                appointment.status
            );

    }


    return `
        <tr>

            <td>

                <div class="fw-semibold">

                    ${formatDateTime(
                        appointment.appointment_time
                    )}

                </div>

            </td>


            <td>

                <div class="fw-semibold">

                    ${escapeHtml(
                        patientName
                    )}

                </div>

                <div class="small text-secondary">

                    ${escapeHtml(
                        patientPhone
                    )}

                </div>

            </td>


            <td>

                #${appointment.patient_id}

            </td>


            <td>

                <div class="fw-semibold">

                    BS.
                    ${escapeHtml(
                        appointment.doctor_name
                    )}

                </div>

            </td>


            <td>

                <span class="text-secondary">

                    ${escapeHtml(
                        appointment.specialty_name
                    )}

                </span>

            </td>


            <td>

                ${renderStatusBadge(
                    appointment.status
                )}

            </td>


            <td class="text-end">

                ${actionHtml}

            </td>

        </tr>
    `;

}


function applyCheckinSearch(
    appointments
) {

    const keyword =
        document
            .getElementById(
                "checkinSearch"
            )
            .value
            .trim()
            .toLowerCase();


    if (!keyword) {

        return appointments;

    }


    return appointments.filter(
        appointment => {

            const patient =
                patientMap[
                    appointment.patient_id
                ];


            const patientName =
                (
                    patient?.full_name ||
                    ""
                ).toLowerCase();


            const patientPhone =
                (
                    patient?.phone ||
                    ""
                ).toLowerCase();


            const doctorName =
                (
                    appointment.doctor_name ||
                    ""
                ).toLowerCase();


            const patientId =
                String(
                    appointment.patient_id
                );


            return (
                patientName.includes(
                    keyword
                ) ||
                patientPhone.includes(
                    keyword
                ) ||
                patientId.includes(
                    keyword
                ) ||
                doctorName.includes(
                    keyword
                )
            );

        }
    );

}


function setupCheckinFilters() {

    const searchInput =
        document.getElementById(
            "checkinSearch"
        );


    searchInput.addEventListener(
        "input",
        () => {

            renderCheckinAppointments(
                allCheckinAppointments
            );

        }
    );

}


async function checkInAppointment(
    appointmentId
) {

    const confirmed =
        confirm(
            "Xác nhận bệnh nhân đã đến và tiếp nhận lịch khám này?"
        );


    if (!confirmed) {

        return;

    }


    try {

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
                "Không thể tiếp nhận bệnh nhân."
            );

        }


        showCheckinAlert(
            "Đã tiếp nhận bệnh nhân thành công.",
            "success"
        );


        await loadCheckinData();

    }
    catch (error) {

        console.error(error);


        showCheckinAlert(
            error.message ||
            "Tiếp nhận bệnh nhân thất bại.",
            "danger"
        );

    }

}


function showCheckinAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "checkinAlert"
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