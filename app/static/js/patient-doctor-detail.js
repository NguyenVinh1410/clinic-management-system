document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await loadDoctorDetail();

            await loadDoctorSchedules();

        }
        catch (error) {

            console.error(
                error
            );

        }

    }
);


async function loadDoctorDetail() {

    const response =
        await apiFetch(
            `/api/doctor/${doctorId}`
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


    renderDoctorDetail(
        data
    );

}


function renderDoctorDetail(
    doctor
) {

    const container =
        document.getElementById(
            "doctorDetail"
        );


    container.innerHTML = `

        <div class="col-12 col-xl-8">

            <div class="content-card">

                <div class="p-4">

                    <div class="d-flex flex-column flex-md-row gap-4">

                        <div
                            class="doctor-avatar"
                            style="
                                width: 88px;
                                height: 88px;
                                font-size: 2rem;
                            ">

                            <i class="bi bi-person-fill"></i>

                        </div>


                        <div>

                            <h2 class="fw-bold mb-2">

                                ${escapeHtml(
                                    doctor.full_name
                                )}

                            </h2>


                            <div
                                class="text-primary fw-semibold mb-3">

                                Bác sĩ chuyên khoa #${doctor.specialty_id}

                            </div>


                            <div class="row g-3">

                                <div class="col-12 col-md-6">

                                    <div class="text-secondary small">
                                        Email
                                    </div>

                                    <div class="fw-semibold">
                                        ${escapeHtml(
                                            doctor.email ||
                                            "Chưa cập nhật"
                                        )}
                                    </div>

                                </div>


                                <div class="col-12 col-md-6">

                                    <div class="text-secondary small">
                                        Số điện thoại
                                    </div>

                                    <div class="fw-semibold">
                                        ${escapeHtml(
                                            doctor.phone ||
                                            "Chưa cập nhật"
                                        )}
                                    </div>

                                </div>


                                <div class="col-12">

                                    <div class="text-secondary small">
                                        Chứng chỉ / bằng cấp
                                    </div>

                                    <div class="fw-semibold">
                                        ${escapeHtml(
                                            doctor.qualification ||
                                            "Chưa cập nhật"
                                        )}
                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>


                    <hr class="my-4">


                    <h5 class="fw-bold mb-2">
                        Giới thiệu
                    </h5>


                    <p class="text-secondary mb-0">

                        ${escapeHtml(
                            doctor.bio ||
                            "Bác sĩ chưa cập nhật phần giới thiệu."
                        )}

                    </p>

                </div>

            </div>

        </div>


        <div class="col-12 col-xl-4">

            <div class="content-card h-100">

                <div class="p-4">

                    <h5 class="fw-bold">
                        Đặt lịch khám
                    </h5>


                    <p class="text-secondary small">

                        Chọn một ca làm việc
                        phù hợp để đặt lịch.

                    </p>


                    <a
                        href="/patient/book-appointment?doctor_id=${doctor.user_id}"
                        class="btn btn-primary w-100">

                        <i class="bi bi-calendar-plus me-2"></i>

                        Đặt lịch với bác sĩ

                    </a>

                </div>

            </div>

        </div>
    `;

}


async function loadDoctorSchedules() {

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


    renderSchedules(
        data
    );

}


function renderSchedules(
    schedules
) {

    const card =
        document.getElementById(
            "doctorSchedule"
        );


    const container =
        document.getElementById(
            "scheduleList"
        );


    card.classList.remove(
        "d-none"
    );


    if (
        !schedules ||
        schedules.length === 0
    ) {

        container.innerHTML = `
            <div class="text-center py-4 text-secondary">

                Không có ca làm việc.

            </div>
        `;

        return;

    }


    container.innerHTML =
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
            .map(
                schedule => `

                    <div
                        class="appointment-card mb-2">

                        <div
                            class="d-flex flex-column flex-md-row justify-content-between gap-3">

                            <div>

                                <div
                                    class="fw-bold">

                                    ${formatDate(
                                        schedule.work_date
                                    )}

                                </div>


                                <div
                                    class="text-secondary">

                                    ${formatTime(
                                        schedule.start_time
                                    )}
                                    -
                                    ${formatTime(
                                        schedule.end_time
                                    )}

                                </div>

                            </div>


                            <div class="d-flex align-items-center gap-2">

                                ${schedule.status === "Active"
                                    ? `
                                        <span class="badge text-bg-success">
                                            Đang hoạt động
                                        </span>
                                    `
                                    : `
                                        <span class="badge text-bg-secondary">
                                            Nghỉ
                                        </span>
                                    `
                                }


                                <a
                                    href="/patient/book-appointment?doctor_id=${doctorId}&schedule_id=${schedule.schedule_id}"
                                    class="btn btn-sm btn-primary">

                                    Chọn ca

                                </a>

                            </div>

                        </div>

                    </div>

                `
            )
            .join("");

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