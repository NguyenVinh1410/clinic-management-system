let invoices = [];

let selectedInvoiceId = null;


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

            setupInvoiceRefresh();

            setupPayment();

        }
        catch (error) {

            console.error(
                error
            );

            showInvoiceAlert(
                error.message ||
                "Không thể tải hóa đơn.",
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
            "Không thể tải hóa đơn."
        );

    }


    invoices =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderInvoices(
        invoices
    );

}


function renderInvoices(
    items
) {

    const tbody =
        document.getElementById(
            "invoiceList"
        );


    if (!items.length) {

        tbody.innerHTML = `
            <tr>

                <td
                    colspan="7"
                    class="text-center
                           py-5
                           text-secondary">

                    Không có hóa đơn.

                </td>

            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        items
            .map(
                invoice => {

                    const statusBadge =
                        invoice.status ===
                        "Paid"

                            ? `
                                <span
                                    class="badge
                                           text-bg-success">

                                    Đã thanh toán

                                </span>
                            `
                            : `
                                <span
                                    class="badge
                                           text-bg-warning">

                                    Chưa thanh toán

                                </span>
                            `;


                    const action =
                        invoice.status ===
                        "Unpaid"

                            ? `
                                <button
                                    type="button"
                                    class="btn
                                           btn-sm
                                           btn-primary"
                                    data-pay-invoice="${invoice.invoice_id}">

                                    <i
                                        class="bi bi-cash-coin me-1">
                                    </i>

                                    Thanh toán

                                </button>
                              `

                            : `
                                <span
                                    class="text-secondary small">

                                    Đã xử lý

                                </span>
                              `;


                    return `
                        <tr>

                            <td>

                                <span
                                    class="fw-semibold">

                                    #${invoice.invoice_id}

                                </span>

                            </td>


                            <td>

                                <div
                                    class="fw-semibold">

                                    ${escapeHtml(
                                        invoice.patient.full_name
                                    )}

                                </div>

                                <div
                                    class="small
                                           text-secondary">

                                    ${
                                        invoice.patient.phone ||
                                        "Chưa có SĐT"
                                    }

                                </div>

                            </td>


                            <td>

                                ${escapeHtml(
                                    invoice.doctor.full_name
                                )}

                            </td>


                            <td>

                                ${formatDateTime(
                                    invoice.appointment_time
                                )}

                            </td>


                            <td>

                                <span
                                    class="fw-semibold">

                                    ${formatCurrency(
                                        invoice.total_amount
                                    )}

                                </span>

                            </td>


                            <td>

                                ${statusBadge}

                            </td>


                            <td
                                class="text-end">

                                ${action}

                            </td>

                        </tr>
                    `;

                }
            )
            .join("");


    bindInvoiceActions();

}


function bindInvoiceActions() {

    document
        .querySelectorAll(
            "[data-pay-invoice]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        openPaymentModal(
                            Number(
                                button.dataset
                                    .payInvoice
                            )
                        );

                    }
                );

            }
        );

}


function openPaymentModal(
    invoiceId
) {

    selectedInvoiceId =
        invoiceId;


    document.getElementById(
        "paymentInvoiceId"
    ).value =
        invoiceId;


    const modalElement =
        document.getElementById(
            "paymentModal"
        );


    const modal =
        bootstrap.Modal.getOrCreateInstance(
            modalElement
        );


    modal.show();

}


function setupPayment() {

    document
        .getElementById(
            "confirmPaymentButton"
        )
        ?.addEventListener(
            "click",
            payInvoice
        );

}


async function payInvoice() {

    if (
        selectedInvoiceId ===
        null
    ) {

        return;

    }


    const paymentMethod =
        document
            .getElementById(
                "paymentMethod"
            )
            .value;


    const response =
        await apiFetch(
            `/api/invoice/${selectedInvoiceId}/pay`,
            {

                method:
                    "PATCH",

                body:
                    JSON.stringify({

                        payment_method:
                            paymentMethod,

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
            "Không thể thanh toán hóa đơn."
        );

    }


    const modal =
        bootstrap.Modal.getInstance(
            document.getElementById(
                "paymentModal"
            )
        );


    modal?.hide();


    showInvoiceAlert(
        "Thanh toán thành công.",
        "success"
    );


    selectedInvoiceId =
        null;


    await loadInvoices();

}


function setupInvoiceFilters() {

    const search =
        document.getElementById(
            "invoiceSearch"
        );


    const status =
        document.getElementById(
            "invoiceStatus"
        );


    function applyFilters() {

        const keyword =
            search.value
                .trim()
                .toLowerCase();


        const selectedStatus =
            status.value;


        const filtered =
            invoices.filter(
                invoice => {

                    const patient =
                        String(
                            invoice.patient
                                ?.full_name ||
                            ""
                        )
                        .toLowerCase();


                    const doctor =
                        String(
                            invoice.doctor
                                ?.full_name ||
                            ""
                        )
                        .toLowerCase();


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
                        invoice.status ===
                        selectedStatus;


                    return (
                        matchSearch &&
                        matchStatus
                    );

                }
            );


        renderInvoices(
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

}


function setupInvoiceRefresh() {

    document
        .getElementById(
            "refreshInvoices"
        )
        ?.addEventListener(
            "click",
            loadInvoices
        );

}


function showInvoiceAlert(
    message,
    type
) {

    const alert =
        document.getElementById(
            "invoiceAlert"
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