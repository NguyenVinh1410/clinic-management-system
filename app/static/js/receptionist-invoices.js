let allInvoices = [];


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

            await loadInvoices();

            setupInvoiceFilters();

            await loadInvoiceFromUrl();

        }
        catch (error) {

            console.error(
                error
            );

            showInvoiceAlert(
                error.message ||
                "Không thể tải trang hóa đơn.",
                "danger"
            );

        }

    }
);

async function loadInvoices() {

    const response =
        await apiFetch(
            "/api/invoice"
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải danh sách hóa đơn."
        );

    }


    allInvoices =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderInvoices(
        allInvoices
    );

}

function renderInvoices(
    invoices
) {

    const tbody =
        document.getElementById(
            "invoiceList"
        );


    document.getElementById(
        "invoiceCount"
    ).textContent =
        `${invoices.length} hóa đơn`;


    if (!invoices.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="7"
                    class="text-center py-5 text-secondary">

                    Chưa có hóa đơn.

                </td>

            </tr>
        `;

        return;
    }


    tbody.innerHTML =
        invoices
            .map(
                invoice =>
                    `
                    <tr>

                        <td>

                            <span class="fw-semibold">

                                #${invoice.invoice_id}

                            </span>

                        </td>


                        <td>

                            <span class="text-secondary">

                                #${invoice.appointment_id}

                            </span>

                        </td>


                        <td>

                            <span class="fw-semibold">

                                ${formatCurrency(
                                    invoice.total_amount
                                )}

                            </span>

                        </td>


                        <td>

                            ${
                                renderInvoiceStatus(
                                    invoice.status
                                )
                            }

                        </td>


                        <td>

                            ${
                                invoice.payment_method ||
                                "—"
                            }

                        </td>


                        <td>

                            ${
                                invoice.paid_at
                                    ? formatDateTime(
                                        invoice.paid_at
                                    )
                                    : "—"
                            }

                        </td>


                        <td class="text-end">

                            <a
                                href="/receptionist/invoices?invoice_id=${invoice.invoice_id}"
                                class="btn btn-sm btn-outline-primary me-1">

                                <i class="bi bi-eye"></i>

                                Xem

                            </a>


                            ${
                                invoice.status === "Unpaid"
                                    ? `
                                        <button
                                            type="button"
                                            class="btn btn-sm btn-success"
                                            onclick="payCash(
                                                ${invoice.invoice_id}
                                            )">

                                            <i class="bi bi-cash-stack me-1"></i>

                                            Thu Cash

                                        </button>
                                    `
                                    : ""
                            }

                        </td>

                    </tr>
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
                class="status-badge status-completed">

                <i class="bi bi-check-circle"></i>

                Đã thanh toán

            </span>
        `;

    }


    return `
        <span
            class="status-badge status-pending">

            <i class="bi bi-clock"></i>

            Chưa thanh toán

        </span>
    `;

}

function setupInvoiceFilters() {

    const searchInput =
        document.getElementById(
            "invoiceSearch"
        );


    const statusSelect =
        document.getElementById(
            "invoiceStatus"
        );


    const applyFilters = () => {

        const keyword =
            searchInput.value
                .trim()
                .toLowerCase();


        const status =
            statusSelect.value;


        const filtered =
            allInvoices.filter(
                invoice => {

                    const matchesSearch =
                        !keyword ||

                        String(
                            invoice.invoice_id
                        ).includes(keyword)

                        ||

                        String(
                            invoice.appointment_id
                        ).includes(keyword);


                    const matchesStatus =
                        !status ||

                        invoice.status ===
                        status;


                    return (
                        matchesSearch &&
                        matchesStatus
                    );

                }
            );


        renderInvoices(
            filtered
        );

    };


    searchInput.addEventListener(
        "input",
        applyFilters
    );


    statusSelect.addEventListener(
        "change",
        applyFilters
    );

}

async function payCash(
    invoiceId
) {

    const confirmed =
        confirm(
            "Xác nhận đã thu tiền mặt cho hóa đơn này?"
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await apiFetch(
                `/api/invoice/${invoiceId}/pay`,
                {
                    method: "PATCH",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({

                        payment_method:
                            "Cash",

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
                "Thanh toán thất bại."
            );

        }


        showInvoiceAlert(
            "Đã thu tiền mặt thành công.",
            "success"
        );


        await loadInvoices();


        const params =
            new URLSearchParams(
                window.location.search
            );


        const invoiceId =
            params.get(
                "invoice_id"
            );


        if (invoiceId) {

            await loadInvoiceDetail(
                invoiceId
            );

        }



    }
    catch (error) {

        console.error(
            error
        );


        showInvoiceAlert(
            error.message ||
            "Không thể thanh toán hóa đơn.",
            "danger"
        );

    }

}

async function loadInvoiceFromUrl() {

    const params =
        new URLSearchParams(
            window.location.search
        );


    const invoiceId =
        params.get(
            "invoice_id"
        );


    if (!invoiceId) {
        return;
    }


    await loadInvoiceDetail(
        invoiceId
    );

}

async function loadInvoiceDetail(
    invoiceId
) {

    const response =
        await apiFetch(
            `/api/invoice/${invoiceId}`
        );


    const data =
        await parseApiResponse(
            response
        );


    if (!response.ok) {

        throw new Error(
            data.detail ||
            "Không thể tải chi tiết hóa đơn."
        );

    }


    renderInvoiceDetail(
        data
    );

}

function renderInvoiceDetail(
    invoice
) {

    const detail =
        document.getElementById(
            "invoiceDetail"
        );


    detail.classList.remove(
        "d-none"
    );


    document.getElementById(
        "detailInvoiceTitle"
    ).textContent =
        `Hóa đơn #${invoice.invoice_id}`;


    document.getElementById(
        "detailAppointmentId"
    ).textContent =
        `#${invoice.appointment_id}`;

    document.getElementById(
        "detailAppointmentTime"
    ).textContent =
        formatDateTime(
            invoice.appointment_time
        );


    document.getElementById(
        "detailPatientName"
    ).textContent =
        invoice.patient.full_name;


    document.getElementById(
        "detailPatientPhone"
    ).textContent =
        invoice.patient.phone ||
        "Chưa cập nhật";


    document.getElementById(
        "detailDoctorName"
    ).textContent =
        invoice.doctor.full_name;


    document.getElementById(
        "detailSpecialtyName"
    ).textContent =
        invoice.specialty.name;


    document.getElementById(
        "detailConsultationFee"
    ).textContent =
        formatCurrency(
            invoice.consultation_fee
        );


    document.getElementById(
        "detailMedicineTotal"
    ).textContent =
        formatCurrency(
            invoice.medicine_total
        );


    document.getElementById(
        "detailTotalBottom"
    ).textContent =
        formatCurrency(
            invoice.total_amount
        );

    document.getElementById(
        "detailTotal"
    ).textContent =
        formatCurrency(
            invoice.total_amount
        );


    document.getElementById(
        "detailStatus"
    ).innerHTML =
        renderInvoiceStatus(
            invoice.status
        );


    document.getElementById(
        "detailPaymentMethod"
    ).textContent =
        invoice.payment_method ||
        "Chưa thanh toán";


    document.getElementById(
        "detailPaidAt"
    ).textContent =
        invoice.paid_at
            ? formatDateTime(
                invoice.paid_at
            )
            : "—";

    renderInvoiceMedicines(
        invoice.medicines
    );

    const payButton =
        document.getElementById(
            "detailPayButton"
        );


    if (invoice.status === "Unpaid") {

        payButton.classList.remove(
            "d-none"
        );


        payButton.onclick =
            () => payCash(
                invoice.invoice_id
            );

    }
    else {

        payButton.classList.add(
            "d-none"
        );

    }


    detail.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });

}

function renderInvoiceMedicines(
    medicines
) {

    const container =
        document.getElementById(
            "detailMedicines"
        );

    if (!medicines.length) {

        container.innerHTML = `
            <div class="text-secondary py-3">
                Hóa đơn không có thuốc.
            </div>
        `;

        return;
    }

    container.innerHTML = `
        <div class="table-responsive">

            <table class="table table-bordered align-middle">

                <thead>

                    <tr>
                        <th>Thuốc</th>
                        <th>SL</th>
                        <th>Đơn giá</th>
                        <th>Thành tiền</th>
                        <th>Liều dùng</th>
                        <th>Cách dùng</th>
                    </tr>

                </thead>

                <tbody>

                    ${medicines
                        .map(
                            medicine => `
                                <tr>

                                    <td>

                                        <div class="fw-semibold">
                                            ${medicine.medicine_name}
                                        </div>

                                        <div class="text-secondary small">
                                            ${medicine.unit}
                                        </div>

                                    </td>

                                    <td>
                                        ${medicine.quantity}
                                    </td>

                                    <td>
                                        ${formatCurrency(
                                            medicine.unit_price
                                        )}
                                    </td>

                                    <td class="fw-semibold">
                                        ${formatCurrency(
                                            medicine.line_total
                                        )}
                                    </td>

                                    <td>
                                        ${medicine.dosage}
                                    </td>

                                    <td>
                                        ${
                                            medicine.usage_note ||
                                            "—"
                                        }
                                    </td>

                                </tr>
                            `
                        )
                        .join("")}

                </tbody>

            </table>

        </div>
    `;
}

function closeInvoiceDetail() {

    const detail =
        document.getElementById(
            "invoiceDetail"
        );


    detail.classList.add(
        "d-none"
    );


    window.history.replaceState(
        {},
        "",
        "/receptionist/invoices"
    );

}