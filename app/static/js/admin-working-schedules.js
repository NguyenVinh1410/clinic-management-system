let doctors = [];
let schedules = [];


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

            await loadDoctors();

            await loadSchedules();

            setupEvents();

            setMinimumDate();

        }
        catch (error) {

            console.error(
                error
            );

            showScheduleAlert(
                error.message ||
                "Không thể tải dữ liệu.",
                "danger"
            );

        }

    }
);

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
            data.detail ||
            "Không thể tải danh sách bác sĩ."
        );

    }


    doctors =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderDoctorOptions();

}

function renderDoctorOptions() {

    const select =
        document.getElementById(
            "doctorId"
        );


    if (!doctors.length) {

        select.innerHTML = `
            <option value="">
                Chưa có bác sĩ
            </option>
        `;

        return;

    }


    select.innerHTML = `
        <option value="">
            Chọn bác sĩ
        </option>

        ${
            doctors
                .filter(
                    doctor =>
                        doctor.status ===
                        "Active"
                )
                .map(
                    doctor => `
                        <option
                            value="${doctor.user_id}">

                            ${escapeHtml(
                                doctor.full_name
                            )}

                        </option>
                    `
                )
                .join("")
        }
    `;

}

async function loadSchedules() {

    const response =
        await apiFetch(
            "/api/working_schedule"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải lịch làm việc."
        );

    }


    schedules =
        Array.isArray(data)
            ? data
            : data.items || [];


    schedules.sort(
        (a, b) => {

            const dateA =
                `${a.work_date} ${a.start_time}`;

            const dateB =
                `${b.work_date} ${b.start_time}`;

            return dateA.localeCompare(
                dateB
            );

        }
    );


    renderSchedules();

}

function renderSchedules() {

    const tbody =
        document.getElementById(
            "scheduleList"
        );


    if (!schedules.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="5"
                    class="text-center
                           py-5
                           text-secondary">

                    Chưa có lịch làm việc.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        schedules
            .map(
                schedule => {

                    const doctor =
                        doctors.find(
                            item =>
                                Number(
                                    item.user_id
                                ) ===
                                Number(
                                    schedule.doctor_id
                                )
                        );


                    const doctorName =
                        doctor?.full_name ||
                        `Bác sĩ #${schedule.doctor_id}`;


                    return `
                        <tr>

                            <td>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        doctorName
                                    )}

                                </div>

                            </td>


                            <td>

                                ${formatScheduleDate(
                                    schedule.work_date
                                )}

                            </td>


                            <td>

                                ${schedule.start_time.slice(0, 5)}
                                -
                                ${schedule.end_time.slice(0, 5)}

                            </td>


                            <td>

                                ${
                                    schedule.status ===
                                    "Active"
                                        ? `
                                            <span
                                                class="badge text-bg-success">

                                                Hoạt động

                                            </span>
                                          `
                                        : `
                                            <span
                                                class="badge text-bg-secondary">

                                                Nghỉ

                                            </span>
                                          `
                                }

                            </td>


                            <td
                                class="text-end">

                                <div
                                    class="d-flex
                                        justify-content-end
                                        gap-2">

                                    <button
                                        type="button"
                                        class="btn
                                            btn-sm
                                            btn-outline-primary"
                                        data-edit-id="${schedule.schedule_id}">
                                        <i class="bi bi-pencil"></i>
                                    </button>

                                    <button
                                        type="button"
                                        class="btn btn-sm btn-outline-danger"
                                        data-delete-id="${schedule.schedule_id}">

                                        <i class="bi bi-trash"></i>

                                    </button>
                                </div>
                            </td>

                        </tr>
                    `;

                }
            )
            .join("");

    tbody
        .querySelectorAll(
            "[data-edit-id]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        editSchedule(
                            Number(
                                button.dataset.editId
                            )
                        );

                    }
                );

            }
        );

    tbody
        .querySelectorAll(
            "[data-delete-id]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        deleteSchedule(
                            Number(
                                button.dataset.deleteId
                            )
                        );

                    }
                );

            }
        );

}

function formatScheduleDate(
    value
) {

    if (!value) {
        return "—";
    }


    const [
        year,
        month,
        day
    ] =
        value.split("-");


    return `${day}/${month}/${year}`;

}

async function createSchedule(
    event
) {

    event.preventDefault();


    const doctorId =
        Number(
            document.getElementById(
                "doctorId"
            ).value
        );


    const workDate =
        document.getElementById(
            "workDate"
        ).value;


    const startTime =
        document.getElementById(
            "startTime"
        ).value;


    const endTime =
        document.getElementById(
            "endTime"
        ).value;


    const status =
        document.getElementById(
            "scheduleStatus"
        ).value;


    if (!doctorId) {

        showScheduleAlert(
            "Vui lòng chọn bác sĩ.",
            "danger"
        );

        return;

    }


    if (!workDate) {

        showScheduleAlert(
            "Vui lòng chọn ngày làm việc.",
            "danger"
        );

        return;

    }


    if (
        startTime >=
        endTime
    ) {

        showScheduleAlert(
            "Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc.",
            "danger"
        );

        return;

    }


    try {

        const response =
            await apiFetch(
                "/api/working_schedule",
                {

                    method: "POST",

                    body: JSON.stringify({

                        doctor_id:
                            doctorId,

                        work_date:
                            workDate,

                        start_time:
                            startTime,

                        end_time:
                            endTime,

                        status:
                            status,

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
                "Không thể tạo lịch làm việc."
            );

        }


        showScheduleAlert(
            "Đã tạo lịch làm việc.",
            "success"
        );


        document
            .getElementById(
                "scheduleForm"
            )
            .reset();


        setMinimumDate();


        await loadSchedules();

    }
    catch (error) {

        console.error(
            error
        );

        showScheduleAlert(
            error.message ||
            "Không thể tạo lịch làm việc.",
            "danger"
        );

    }

}

async function editSchedule(
    scheduleId
) {

    const schedule =
        schedules.find(
            item =>
                Number(
                    item.schedule_id
                ) ===
                Number(
                    scheduleId
                )
        );


    if (!schedule) {

        showScheduleAlert(
            "Không tìm thấy lịch làm việc.",
            "danger"
        );

        return;

    }


    const workDate =
        window.prompt(
            "Ngày làm việc (YYYY-MM-DD):",
            schedule.work_date
        );


    if (workDate === null) {

        return;

    }


    const startTime =
        window.prompt(
            "Giờ bắt đầu (HH:MM):",
            schedule.start_time.slice(
                0,
                5
            )
        );


    if (startTime === null) {

        return;

    }


    const endTime =
        window.prompt(
            "Giờ kết thúc (HH:MM):",
            schedule.end_time.slice(
                0,
                5
            )
        );


    if (endTime === null) {

        return;

    }


    const status =
        window.prompt(
            "Trạng thái: Active hoặc Off",
            schedule.status
        );


    if (status === null) {

        return;

    }


    if (
        !["Active", "Off"]
            .includes(status)
    ) {

        showScheduleAlert(
            "Trạng thái chỉ được Active hoặc Off.",
            "danger"
        );

        return;

    }


    if (
        startTime >=
        endTime
    ) {

        showScheduleAlert(
            "Giờ bắt đầu phải nhỏ hơn giờ kết thúc.",
            "danger"
        );

        return;

    }


    try {

        const response =
            await apiFetch(
                `/api/working_schedule/${scheduleId}`,
                {

                    method: "PATCH",

                    body: JSON.stringify({

                        work_date:
                            workDate,

                        start_time:
                            startTime,

                        end_time:
                            endTime,

                        status:
                            status,

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
                "Không thể cập nhật lịch."
            );

        }


        showScheduleAlert(
            "Đã cập nhật lịch làm việc.",
            "success"
        );


        await loadSchedules();

    }
    catch (error) {

        console.error(
            error
        );


        showScheduleAlert(
            error.message ||
            "Không thể cập nhật lịch.",
            "danger"
        );

    }

}

async function deleteSchedule(
    scheduleId
) {

    const confirmed =
        window.confirm(
            "Bạn có chắc muốn xóa lịch làm việc này?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await apiFetch(
                `/api/working_schedule/${scheduleId}`,
                {
                    method: "DELETE",
                }
            );


        if (!response.ok) {

            const data =
                await parseApiResponse(
                    response
                );


            throw new Error(
                data.detail ||
                "Không thể xóa lịch làm việc."
            );

        }


        showScheduleAlert(
            "Đã xóa lịch làm việc.",
            "success"
        );


        await loadSchedules();

    }
    catch (error) {

        console.error(
            error
        );


        showScheduleAlert(
            error.message ||
            "Không thể xóa lịch.",
            "danger"
        );

    }

}

function setupEvents() {

    document
        .getElementById(
            "scheduleForm"
        )
        .addEventListener(
            "submit",
            createSchedule
        );


    document
        .getElementById(
            "refreshSchedules"
        )
        .addEventListener(
            "click",
            async () => {

                try {

                    await loadDoctors();

                    await loadSchedules();

                }
                catch (error) {

                    showScheduleAlert(
                        error.message ||
                        "Không thể làm mới.",
                        "danger"
                    );

                }

            }
        );


    const sidebar =
        document.getElementById(
            "sidebar"
        );


    const toggle =
        document.getElementById(
            "sidebarToggle"
        );


    toggle?.addEventListener(
        "click",
        () => {

            sidebar.classList.toggle(
                "show"
            );

        }
    );

}

function setMinimumDate() {

    const input =
        document.getElementById(
            "workDate"
        );


    if (!input) {
        return;
    }


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


    input.min =
        `${year}-${month}-${day}`;

}

function showScheduleAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "scheduleAlert"
        );


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );


    setTimeout(
        () => {

            alert.classList.add(
                "d-none"
            );

        },
        4000
    );

}