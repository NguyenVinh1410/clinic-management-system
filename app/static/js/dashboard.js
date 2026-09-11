let appointmentsChart = null;
let revenueChart = null;
let specialtyChart = null;
let appointmentStatusChart = null;


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        if (!isAuthenticated()) {

            window.location.href =
                "/login";

            return;

        }


        setupSidebarToggle();

        setTodayText();


        try {

            const currentUser =
                await loadCurrentUser();


            setupUserInfo(
                currentUser
            );


            if (
                currentUser.role ===
                "Admin"
            ) {

                document
                    .getElementById(
                        "adminDashboard"
                    )
                    .classList
                    .remove("d-none");


                await loadAdminDashboard();

            }
            else {

                setupRoleDashboard(
                    currentUser
                );

            }

        }
        catch (error) {

            console.error(
                error
            );


            showDashboardAlert(
                "Không thể tải dữ liệu dashboard.",
                "danger"
            );

        }

    }
);


function setupSidebarToggle() {

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


function setTodayText() {

    const element =
        document.getElementById(
            "todayText"
        );


    element.textContent =
        new Date().toLocaleDateString(
            "vi-VN",
            {
                weekday: "long",
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            }
        );

}


async function loadCurrentUser() {

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
            "Unable to load user"
        );

    }


    sessionStorage.setItem(
        "current_user",
        JSON.stringify(data)
    );


    return data;

}


function setupUserInfo(
    user
) {

    const role =
        String(
            user.role || ""
        );


    document.getElementById(
        "welcomeName"
    ).textContent =
        user.full_name ||
        user.username;


    document.getElementById(
        "sidebarUserName"
    ).textContent =
        user.full_name ||
        user.username;


    document.getElementById(
        "topUserName"
    ).textContent =
        user.full_name ||
        user.username;


    document.getElementById(
        "topUserRole"
    ).textContent =
        role;


    document.getElementById(
        "profileName"
    ).textContent =
        user.full_name || "-";


    document.getElementById(
        "profileUsername"
    ).textContent =
        user.username || "-";


    document.getElementById(
        "profileEmail"
    ).textContent =
        user.email || "-";


    document.getElementById(
        "profileRole"
    ).textContent =
        role;


    const initials =
        (
            user.full_name ||
            user.username ||
            "U"
        )
        .trim()
        .split(/\s+/)
        .slice(-2)
        .map(
            part =>
                part.charAt(0)
                    .toUpperCase()
        )
        .join("");


    document.getElementById(
        "userAvatar"
    ).textContent =
        initials;


    document
        .querySelectorAll(
            ".role-link"
        )
        .forEach(
            link =>
                link.classList.add(
                    "d-none"
                )
        );


    const roleClass =
        {
            Admin:
                "role-admin",

            Receptionist:
                "role-receptionist",

            Doctor:
                "role-doctor",

            Patient:
                "role-patient",
        }[role];


    if (roleClass) {

        document
            .querySelectorAll(
                `.${roleClass}`
            )
            .forEach(
                link =>
                    link.classList.remove(
                        "d-none"
                    )
            );

    }

}


function setupRoleDashboard(
    user
) {

    document
        .getElementById(
            "roleDashboard"
        )
        .classList
        .remove("d-none");


    const configs = {

        Receptionist: {

            title:
                "Khu vực lễ tân",

            text:
                "Lễ tân sẽ quản lý bệnh nhân, lịch hẹn, tiếp nhận và thanh toán.",

        },


        Doctor: {

            title:
                "Khu vực bác sĩ",

            text:
                "Bác sĩ sẽ theo dõi lịch khám, bệnh nhân, hồ sơ bệnh án, lịch sử khám và đơn thuốc.",

        },


        Patient: {

            title:
                "Khu vực bệnh nhân",

            text:
                "Bệnh nhân sẽ quản lý hồ sơ cá nhân, lịch hẹn, hóa đơn và trợ lý AI.",

        },

    };


    const config =
        configs[user.role];


    if (!config) {

        return;

    }


    document.getElementById(
        "roleDashboardTitle"
    ).textContent =
        config.title;


    document.getElementById(
        "roleDashboardText"
    ).textContent =
        config.text;

}


async function loadAdminDashboard() {

    const response =
        await apiFetch(
            "/api/dashboard"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không tải được dashboard"
        );

    }


    renderSummary(
        data.summary
    );


    renderAppointmentsChart(
        data.appointments_by_month
    );


    renderRevenueChart(
        data.revenue_by_month
    );


    renderSpecialtyChart(
        data.appointments_by_specialty
    );


    renderAppointmentStatusChart(
        data.appointments_by_status
    );


    renderTopDoctors(
        data.top_doctors
    );

}


function renderSummary(
    summary
) {

    document.getElementById(
        "totalPatients"
    ).textContent =
        summary.total_patients || 0;


    document.getElementById(
        "todayAppointments"
    ).textContent =
        summary.today_appointments || 0;


    document.getElementById(
        "monthlyRevenue"
    ).textContent =
        formatCurrency(
            summary.monthly_revenue
        );


    document.getElementById(
        "pendingAppointments"
    ).textContent =
        summary.pending_appointments || 0;


    document.getElementById(
        "welcomeMessage"
    ).textContent =
        "Tổng quan hoạt động của phòng khám theo dữ liệu hiện tại.";

}


function renderAppointmentsChart(
    items
) {

    const labels =
        items.map(
            item => item.month
        );


    const values =
        items.map(
            item => item.total
        );


    if (appointmentsChart) {

        appointmentsChart.destroy();

    }


    appointmentsChart =
        new Chart(
            document.getElementById(
                "appointmentsChart"
            ),
            {
                type: "line",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Lượt khám",

                            data:
                                values,

                            tension:
                                0.35,

                            fill:
                                true,

                        },

                    ],

                },

                options:
                    commonChartOptions(),
            }
        );

}


function renderRevenueChart(
    items
) {

    const labels =
        items.map(
            item => item.month
        );


    const values =
        items.map(
            item =>
                Number(
                    item.value || 0
                )
        );


    if (revenueChart) {

        revenueChart.destroy();

    }


    revenueChart =
        new Chart(
            document.getElementById(
                "revenueChart"
            ),
            {
                type: "bar",

                data: {

                    labels,

                    datasets: [

                        {

                            label:
                                "Doanh thu",

                            data:
                                values,

                            borderRadius:
                                8,

                        },

                    ],

                },

                options:
                    commonChartOptions(),
            }
        );

}


function renderSpecialtyChart(
    items
) {

    const labels =
        items.map(
            item =>
                item.specialty_name
        );


    const values =
        items.map(
            item =>
                item.total
        );


    if (specialtyChart) {

        specialtyChart.destroy();

    }


    specialtyChart =
        new Chart(
            document.getElementById(
                "specialtyChart"
            ),
            {
                type:
                    "doughnut",

                data: {

                    labels,

                    datasets: [

                        {

                            data:
                                values,

                        },

                    ],

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                        },

                    },

                },

            }
        );

}


function renderAppointmentStatusChart(
    items
) {

    const labels =
        items.map(
            item =>
                item.status
        );


    const values =
        items.map(
            item =>
                item.total
        );


    if (
        appointmentStatusChart
    ) {

        appointmentStatusChart
            .destroy();

    }


    appointmentStatusChart =
        new Chart(
            document.getElementById(
                "appointmentStatusChart"
            ),
            {
                type:
                    "doughnut",

                data: {

                    labels,

                    datasets: [

                        {

                            data:
                                values,

                        },

                    ],

                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    plugins: {

                        legend: {

                            position:
                                "bottom",

                        },

                    },

                },

            }
        );

}


function renderTopDoctors(
    items
) {

    const tbody =
        document.getElementById(
            "topDoctorsBody"
        );


    if (
        !items ||
        items.length === 0
    ) {

        tbody.innerHTML = `
            <tr>
                <td
                    colspan="3"
                    class="text-center text-secondary py-4">
                    Chưa có dữ liệu
                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        items.map(
            (item, index) => `

                <tr>

                    <td>

                        <span class="fw-bold">

                            ${index + 1}

                        </span>

                    </td>


                    <td class="fw-semibold">

                        ${escapeHtml(
                            item.doctor_name
                        )}

                    </td>


                    <td class="text-end fw-semibold">

                        ${item.total}

                    </td>

                </tr>

            `
        ).join("");

}


function commonChartOptions() {

    return {

        responsive:
            true,

        maintainAspectRatio:
            false,

        plugins: {

            legend: {

                position:
                    "top",

            },

        },

        scales: {

            y: {

                beginAtZero:
                    true,

                ticks: {

                    precision:
                        0,

                },

            },

        },

    };

}


function showDashboardAlert(
    message,
    type = "danger"
) {

    const alertBox =
        document.getElementById(
            "dashboardAlert"
        );


    alertBox.className =
        `alert alert-${type}`;


    alertBox.textContent =
        message;


    alertBox.classList.remove(
        "d-none"
    );

}