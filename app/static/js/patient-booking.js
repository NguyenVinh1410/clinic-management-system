let doctors = [];
let schedules = [];

let selectedDoctor = null;
let selectedSchedule = null;
let selectedSlot = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await loadHeader();

            await loadDoctors();

            setupEvents();


            /*
             * Trường hợp:
             * /patient/book-appointment
             */
            if (!initialDoctorId) {

                updateSummary();

                return;

            }


            /*
             * Trường hợp:
             * /patient/book-appointment?doctor_id=3
             */
            const doctorId =
                Number(initialDoctorId);


            selectedDoctor =
                doctors.find(
                    doctor =>
                        doctor.user_id ===
                        doctorId
                );


            if (!selectedDoctor) {

                showBookingAlert(
                    "Không tìm thấy bác sĩ.",
                    "danger"
                );

                return;

            }


            document.getElementById(
                "doctorSelect"
            ).value =
                doctorId;


            updateSummary();


            /*
             * Load ca làm việc của bác sĩ
             */
            await loadSchedules(
                doctorId
            );


            /*
             * Trường hợp:
             * /patient/book-appointment
             * ?doctor_id=3
             * &schedule_id=4
             */
            if (initialScheduleId) {

                const scheduleId =
                    Number(
                        initialScheduleId
                    );


                const exists =
                    schedules.some(
                        schedule =>
                            schedule.schedule_id ===
                            scheduleId
                    );


                if (exists) {

                    document.getElementById(
                        "scheduleSelect"
                    ).value =
                        scheduleId;


                    await selectSchedule(
                        scheduleId
                    );

                }
                else {

                    showBookingAlert(
                        "Ca làm việc không thuộc bác sĩ đã chọn.",
                        "warning"
                    );

                }

            }

        }
        catch (error) {

            console.error(
                error
            );

            showBookingAlert(
                "Không thể tải dữ liệu đặt lịch.",
                "danger"
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


async function loadDoctors() {

    const response =
        await apiFetch(
            "/api/doctor"
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


    doctors = data;


    const select =
        document.getElementById(
            "doctorSelect"
        );


    doctors.forEach(
        doctor => {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                doctor.user_id;


            option.textContent =
                doctor.full_name;


            select.appendChild(
                option
            );

        }
    );

}


function setupEvents() {

    document.getElementById(
        "doctorSelect"
    ).addEventListener(
        "change",
        async event => {

            const doctorId =
                Number(
                    event.target.value
                );


            resetBookingAfterDoctor();


            if (!doctorId) {

                return;

            }


            selectedDoctor =
                doctors.find(
                    doctor =>
                        doctor.user_id ===
                        doctorId
                );


            await loadSchedules(
                doctorId
            );

        }
    );


    document.getElementById(
        "scheduleSelect"
    ).addEventListener(
        "change",
        async event => {

            const scheduleId =
                Number(
                    event.target.value
                );


            if (!scheduleId) {

                return;

            }


            await selectSchedule(
                scheduleId
            );

        }
    );


    document.getElementById(
        "confirmBookingButton"
    ).addEventListener(
        "click",
        createAppointment
    );

}


async function loadSchedules(
    doctorId
) {

    const response =
        await apiFetch(
            `/api/working_schedule/doctor/${doctorId}`
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

    const today = getLocalDateString();

    schedules =
        data.filter(
            schedule =>
                schedule.status === "Active" &&
                schedule.work_date >= today
        );


    const select =
        document.getElementById(
            "scheduleSelect"
        );


    select.innerHTML = `
        <option value="">
            -- Chọn ca làm việc --
        </option>
    `;


    schedules
        .sort(
            (a, b) =>
                new Date(
                    `${a.work_date}T${a.start_time}`
                ) -
                new Date(
                    `${b.work_date}T${b.start_time}`
                )
        )
        .forEach(
            schedule => {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    schedule.schedule_id;


                option.textContent =
                    `${formatDate(
                        schedule.work_date
                    )} · ${
                        formatTime(
                            schedule.start_time
                        )
                    } - ${
                        formatTime(
                            schedule.end_time
                        )
                    }`;


                select.appendChild(
                    option
                );

            }
        );


    select.disabled =
        schedules.length === 0;

}


async function selectSchedule(
    scheduleId
) {

    selectedSchedule =
        schedules.find(
            schedule =>
                schedule.schedule_id ===
                scheduleId
        );

    if (!selectedSchedule) {
        return;
    }

    selectedSlot = null;

    const bookedTimes =
        await loadBookedAppointmentsForSchedule(
            scheduleId
        );

    renderSlots(
        selectedSchedule,
        bookedTimes
    );

    updateSummary();
}

async function loadBookedAppointmentsForSchedule(
    scheduleId
) {

    const response =
        await apiFetch(
            `/api/appointment/schedule/${scheduleId}/booked-times`
        );

    const data =
        await parseApiResponse(
            response
        );

    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải các khung giờ đã đặt."
        );

    }

    return Array.isArray(data)
        ? data
        : [];
}

function renderSlots(
    schedule,
    bookedTimes = []
) {

    const container =
        document.getElementById(
            "slotGrid"
        );


    const start =
        combineDateTime(
            schedule.work_date,
            schedule.start_time
        );


    const end =
        combineDateTime(
            schedule.work_date,
            schedule.end_time
        );


    const slots = [];


    let current =
        new Date(start);


    while (
        current.getTime() +
        30 * 60 * 1000 <=
        end.getTime()
    ) {

        slots.push(
            new Date(current)
        );

        current =
            new Date(
                current.getTime() +
                30 * 60 * 1000
            );

    }


    if (slots.length === 0) {

        container.innerHTML = `
            <div class="text-secondary">
                Ca làm việc không có slot hợp lệ.
            </div>
        `;

        return;
    }


    const now = new Date();

    const bookedSet = new Set(
        bookedTimes.map(
            value =>
                toLocalISOString(
                    new Date(value)
                )
        )
    );


    container.innerHTML =
        slots
            .map(
                slot => {

                    const iso =
                        toLocalISOString(
                            slot
                        );

                    const isBooked =
                        bookedSet.has(iso);

                    const isPast =
                        slot.getTime() <=
                        now.getTime();

                    const disabled =
                        isBooked || isPast;

                    const statusText =
                        isBooked
                            ? " · Đã đặt"
                            : isPast
                                ? " · Đã qua"
                                : "";

                    return `
                        <button
                            type="button"
                            class="slot-button ${
                                disabled
                                    ? "disabled"
                                    : ""
                            }"
                            data-slot="${iso}"
                            ${
                                disabled
                                    ? "disabled"
                                    : ""
                            }>

                            ${slot.toLocaleTimeString(
                                "vi-VN",
                                {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                }
                            )}${statusText}

                        </button>
                    `;
                }
            )
            .join("");


    container
        .querySelectorAll(
            ".slot-button:not(:disabled)"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        container
                            .querySelectorAll(
                                ".slot-button"
                            )
                            .forEach(
                                item =>
                                    item.classList.remove(
                                        "selected"
                                    )
                            );


                        button.classList.add(
                            "selected"
                        );


                        selectedSlot =
                            button.dataset.slot;


                        updateSummary();

                    }
                );

            }
        );

}


async function createAppointment() {

    if (
        !selectedSchedule ||
        !selectedSlot
    ) {

        showBookingAlert(
            "Vui lòng chọn đầy đủ bác sĩ, ca làm việc và thời gian.",
            "warning"
        );

        return;

    }


    const button =
        document.getElementById(
            "confirmBookingButton"
        );


    button.disabled =
        true;


    try {

        const note =
            document.getElementById(
                "appointmentNote"
            )
            .value
            .trim();


        const response =
            await apiFetch(
                "/api/appointment",
                {
                    method: "POST",

                    body: JSON.stringify({
                        schedule_id:
                            selectedSchedule.schedule_id,

                        appointment_time:
                            selectedSlot,

                        note:
                            note || null,
                    }),
                }
            );


        const data =
            await parseApiResponse(
                response
            );


        if (!response.ok) {

            showBookingAlert(
                typeof data === "object"
                    ? data.detail ||
                      "Không thể đặt lịch."
                    : "Không thể đặt lịch.",
                "danger"
            );

            return;

        }


        showBookingAlert(
            "Đặt lịch thành công!",
            "success"
        );


        setTimeout(
            () => {

                window.location.href =
                    "/patient/appointments";

            },
            800
        );

    }
    catch (error) {

        console.error(
            error
        );


        showBookingAlert(
            "Không thể kết nối tới máy chủ.",
            "danger"
        );

    }
    finally {

        button.disabled =
            false;

    }

}


function updateSummary() {

    document.getElementById(
        "summaryDoctor"
    ).textContent =
        selectedDoctor
            ? selectedDoctor.full_name
            : "Chưa chọn";


    document.getElementById(
        "summaryDate"
    ).textContent =
        selectedSchedule
            ? formatDate(
                selectedSchedule.work_date
            )
            : "Chưa chọn";


    document.getElementById(
        "summaryTime"
    ).textContent =
        selectedSlot
            ? new Date(
                selectedSlot
            ).toLocaleTimeString(
                "vi-VN",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                }
            )
            : "Chưa chọn";


    document.getElementById(
        "confirmBookingButton"
    ).disabled =
        !(
            selectedDoctor &&
            selectedSchedule &&
            selectedSlot
        );

}


function resetBookingAfterDoctor() {

    selectedSchedule = null;

    selectedSlot = null;


    document.getElementById(
        "scheduleSelect"
    ).innerHTML = `
        <option value="">
            -- Chọn ca làm việc --
        </option>
    `;


    document.getElementById(
        "scheduleSelect"
    ).disabled =
        true;


    document.getElementById(
        "slotGrid"
    ).innerHTML = `
        <div class="text-secondary small">
            Vui lòng chọn ca làm việc trước.
        </div>
    `;


    updateSummary();

}


function showBookingAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "bookingAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}


function combineDateTime(
    date,
    time
) {

    return new Date(
        `${date}T${time}`
    );

}


function toLocalISOString(
    date
) {

    const pad =
        value =>
            String(value).padStart(
                2,
                "0"
            );


    return `${date.getFullYear()}-${pad(
        date.getMonth() + 1
    )}-${pad(
        date.getDate()
    )}T${pad(
        date.getHours()
    )}:${pad(
        date.getMinutes()
    )}:00`;

}


function formatDate(
    value
) {

    return new Date(
        `${value}T00:00:00`
    ).toLocaleDateString(
        "vi-VN",
        {
            weekday: "long",
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
        }
    );

}


function formatTime(
    value
) {

    return value.slice(
        0,
        5
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
        ).padStart(2, "0");

    const day =
        String(
            now.getDate()
        ).padStart(2, "0");

    return `${year}-${month}-${day}`;
}