function getInitials(name) {

    if (!name) {
        return "U";
    }

    return name
        .trim()
        .split(/\s+/)
        .slice(-2)
        .map(
            item =>
                item
                    .charAt(0)
                    .toUpperCase()
        )
        .join("");
}


function formatDateTime(value) {

    if (!value) {
        return "—";
    }

    const date =
        new Date(value);


    if (Number.isNaN(date.getTime())) {
        return "—";
    }


    return date.toLocaleString(
        "vi-VN",
        {
            dateStyle: "short",
            timeStyle: "short",
        }
    );

}


function renderStatusBadge(status) {

    const config = {

        Pending: {
            text: "Chờ xác nhận",
            className: "status-pending",
            icon: "bi-clock",
        },

        Confirmed: {
            text: "Đã xác nhận",
            className: "status-confirmed",
            icon: "bi-check-circle",
        },

        Completed: {
            text: "Đã hoàn thành",
            className: "status-completed",
            icon: "bi-check2-all",
        },

        Cancelled: {
            text: "Đã hủy",
            className: "status-cancelled",
            icon: "bi-x-circle",
        },

    };


    const item =
        config[status] || {

            text: status || "Không xác định",

            className: "",

            icon: "bi-info-circle",

        };


    return `
        <span
            class="status-badge ${item.className}">

            <i
                class="bi ${item.icon}">
            </i>

            ${item.text}

        </span>
    `;

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
            data.detail ||
            "Không thể lấy tài khoản."
        );

    }


    const name =
        data.full_name ||
        data.username ||
        "Người dùng";


    const sidebarName =
        document.getElementById(
            "sidebarUserName"
        );


    if (sidebarName) {

        sidebarName.textContent =
            name;

    }


    const topName =
        document.getElementById(
            "topUserName"
        );


    if (topName) {

        topName.textContent =
            name;

    }


    const avatar =
        document.getElementById(
            "userAvatar"
        );


    if (avatar) {

        avatar.textContent =
            getInitials(name);

    }


    return data;

}