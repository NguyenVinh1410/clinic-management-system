let patientInvoices = [];


document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await loadHeader();

            await loadInvoices();

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


async function loadInvoices() {

    const response =
        await apiFetch(
            "/api/invoice/my"
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


    patientInvoices =
        Array.isArray(data)
            ? data
            : data.items || [];


    renderInvoices();

}


function renderInvoices() {

    const container =
        document.getElementById(
            "invoiceList"
        );


    if (
        patientInvoices.length === 0
    ) {

        container.innerHTML = `
            <div class="content-card">

                <div class="text-center py-5 text-secondary">

                    <i class="bi bi-receipt fs-1 d-block mb-3"></i>

                    Bạn chưa có hóa đơn.

                </div>

            </div>
        `;

        return;

    }


    container.innerHTML =
        patientInvoices
            .map(
                invoice =>
                    `

                    <div class="content-card mb-3">

                        <div
                            class="p-4">

                            <div
                                class="d-flex flex-column flex-md-row justify-content-between gap-3">

                                <div>

                                    <div
                                        class="d-flex align-items-center gap-2 mb-2">

                                        <div
                                            class="stat-icon icon-primary"
                                            style="
                                                width:42px;
                                                height:42px;
                                            ">

                                            <i class="bi bi-receipt"></i>

                                        </div>


                                        <div>

                                            <h5 class="fw-bold mb-0">

                                                Hóa đơn
                                                #${invoice.invoice_id}

                                            </h5>


                                            <div
                                                class="small text-secondary">

                                                Lịch khám
                                                #${invoice.appointment_id}

                                            </div>

                                        </div>

                                    </div>

                                </div>


                                <div
                                    class="text-md-end">

                                    <div
                                        class="small text-secondary">

                                        Tổng tiền

                                    </div>


                                    <div
                                        class="fs-4 fw-bold">

                                        ${formatCurrency(
                                            invoice.total_amount
                                        )}

                                    </div>

                                </div>

                            </div>


                            <hr>


                            <div
                                class="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">

                                <div>

                                    ${
                                        invoice.status === "Paid"
                                            ? `
                                                <span class="badge text-bg-success">

                                                    Đã thanh toán

                                                </span>
                                              `
                                            : `
                                                <span class="badge text-bg-warning">

                                                    Chưa thanh toán

                                                </span>
                                              `
                                    }

                                    ${
                                        invoice.paid_at
                                            ? `
                                                <div
                                                    class="small text-secondary mt-2">

                                                    Thanh toán:
                                                    ${formatDateTime(
                                                        invoice.paid_at
                                                    )}

                                                </div>
                                              `
                                            : ""
                                    }

                                </div>


                                <div>

                                    ${
                                        invoice.status === "Unpaid"
                                            ? `
                                                <button
                                                    type="button"
                                                    class="btn btn-primary"
                                                    data-pay-id="${invoice.invoice_id}">

                                                    <i class="bi bi-credit-card me-2"></i>

                                                    Thanh toán Online

                                                </button>
                                              `
                                            : `
                                                <button
                                                    type="button"
                                                    class="btn btn-light"
                                                    disabled>

                                                    Đã thanh toán

                                                </button>
                                              `
                                    }

                                </div>

                            </div>

                        </div>

                    </div>

                    `
            )
            .join("");


    container
        .querySelectorAll(
            "[data-pay-id]"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        payInvoice(
                            Number(
                                button.dataset.payId
                            ),
                            button
                        );

                    }
                );

            }
        );

}


async function payInvoice(
    invoiceId,
    button
) {

    const confirmed =
        window.confirm(
            "Xác nhận thanh toán online cho hóa đơn này?"
        );


    if (!confirmed) {

        return;

    }


    button.disabled =
        true;


    try {

        const response =
            await apiFetch(
                `/api/invoice/${invoiceId}/pay`,
                {
                    method: "PATCH",

                    body: JSON.stringify({
                        payment_method:
                            "Online",
                    }),
                }
            );


        const data =
            await parseApiResponse(
                response
            );


        if (!response.ok) {

            showInvoiceAlert(
                typeof data === "object"
                    ? data.detail ||
                      "Thanh toán thất bại."
                    : "Thanh toán thất bại.",
                "danger"
            );

            return;

        }


        showInvoiceAlert(
            "Thanh toán online thành công.",
            "success"
        );


        await loadInvoices();

    }
    catch (error) {

        console.error(
            error
        );


        showInvoiceAlert(
            "Không thể kết nối tới máy chủ.",
            "danger"
        );

    }
    finally {

        button.disabled =
            false;

    }

}


function formatCurrency(
    value
) {

    return new Intl.NumberFormat(
        "vi-VN",
        {
            style: "currency",
            currency: "VND",
            maximumFractionDigits: 0,
        }
    ).format(
        Number(value || 0)
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


    alert.className =
        `alert alert-${type}`;


    alert.textContent =
        message;


    alert.classList.remove(
        "d-none"
    );

}