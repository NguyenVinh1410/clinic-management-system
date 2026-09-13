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
            <div
                class="content-card">

                <div
                    class="text-center
                           py-5
                           text-secondary">

                    <i
                        class="bi
                               bi-receipt
                               fs-1
                               d-block
                               mb-3">
                    </i>

                    Bạn chưa có hóa đơn.

                </div>

            </div>
        `;

        return;

    }


    container.innerHTML =
        patientInvoices
            .map(
                invoice => {

                    const isPaid =
                        invoice.status === "Paid";


                    return `
                        <div
                            class="content-card mb-4">

                            <div
                                class="p-4
                                       border-bottom">

                                <div
                                    class="d-flex
                                           justify-content-between
                                           gap-3
                                           flex-wrap">

                                    <div>

                                        <h5
                                            class="fw-bold mb-1">

                                            Hóa đơn
                                            #${invoice.invoice_id}

                                        </h5>


                                        <div
                                            class="small
                                                   text-secondary">

                                            Lịch khám
                                            #${invoice.appointment_id}

                                        </div>


                                        <div
                                            class="small
                                                   text-secondary
                                                   mt-1">

                                            ${formatDateTime(
                                                invoice.appointment_time
                                            )}

                                        </div>

                                    </div>


                                    <div>

                                        ${
                                            isPaid
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
                                                  `
                                        }

                                    </div>

                                </div>

                            </div>


                            <div class="p-4">

                                <div
                                    class="row g-3">

                                    <div
                                        class="col-12
                                               col-md-4">

                                        <div
                                            class="text-secondary
                                                   small">

                                            Tiền khám

                                        </div>

                                        <div
                                            class="fw-semibold
                                                   mt-1">

                                            ${formatCurrency(
                                                invoice.consultation_fee
                                            )}

                                        </div>

                                    </div>


                                    <div
                                        class="col-12
                                               col-md-4">

                                        <div
                                            class="text-secondary
                                                   small">

                                            Tiền thuốc

                                        </div>

                                        <div
                                            class="fw-semibold
                                                   mt-1">

                                            ${formatCurrency(
                                                invoice.medicine_total
                                            )}

                                        </div>

                                    </div>


                                    <div
                                        class="col-12
                                               col-md-4">

                                        <div
                                            class="text-secondary
                                                   small">

                                            Tổng tiền

                                        </div>

                                        <div
                                            class="fw-bold
                                                   fs-5
                                                   mt-1">

                                            ${formatCurrency(
                                                invoice.total_amount
                                            )}

                                        </div>

                                    </div>

                                </div>


                                ${
                                    invoice.medicines &&
                                    invoice.medicines.length
                                        ? `
                                            <hr>

                                            <div>

                                                <div
                                                    class="fw-semibold
                                                           mb-3">

                                                    Chi tiết thuốc

                                                </div>


                                                <div
                                                    class="table-responsive">

                                                    <table
                                                        class="table
                                                               table-sm
                                                               align-middle">

                                                        <thead>

                                                            <tr>

                                                                <th>
                                                                    Thuốc
                                                                </th>

                                                                <th>
                                                                    SL
                                                                </th>

                                                                <th>
                                                                    Đơn giá
                                                                </th>

                                                                <th>
                                                                    Thành tiền
                                                                </th>

                                                            </tr>

                                                        </thead>


                                                        <tbody>

                                                            ${
                                                                invoice.medicines
                                                                    .map(
                                                                        medicine => `
                                                                            <tr>

                                                                                <td>

                                                                                    ${escapeHtml(
                                                                                        medicine.medicine_name
                                                                                    )}

                                                                                </td>

                                                                                <td>

                                                                                    ${medicine.quantity}

                                                                                </td>

                                                                                <td>

                                                                                    ${formatCurrency(
                                                                                        medicine.unit_price
                                                                                    )}

                                                                                </td>

                                                                                <td>

                                                                                    ${formatCurrency(
                                                                                        medicine.line_total
                                                                                    )}

                                                                                </td>

                                                                            </tr>
                                                                        `
                                                                    )
                                                                    .join("")
                                                            }

                                                        </tbody>

                                                    </table>

                                                </div>

                                            </div>
                                          `
                                        : ""
                                }

                            </div>


                            <div
                                class="p-4
                                       border-top
                                       d-flex
                                       justify-content-between
                                       align-items-center
                                       gap-3
                                       flex-wrap">

                                <div>

                                    ${
                                        isPaid
                                            ? `
                                                <div
                                                    class="small
                                                           text-secondary">

                                                    Phương thức:
                                                    ${
                                                        invoice.payment_method ||
                                                        "—"
                                                    }

                                                </div>


                                                <div
                                                    class="small
                                                           text-secondary">

                                                    Thanh toán:
                                                    ${formatDateTime(
                                                        invoice.paid_at
                                                    )}

                                                </div>
                                              `
                                            : `
                                                <div
                                                    class="small
                                                           text-secondary">

                                                    Phương thức thanh toán:

                                                </div>

                                                <div
                                                    class="fw-semibold">

                                                    Online

                                                </div>
                                              `
                                    }

                                </div>


                                ${
                                    !isPaid
                                        ? `
                                            <button
                                                type="button"
                                                class="btn btn-primary"
                                                data-pay-id="${invoice.invoice_id}">

                                                <i
                                                    class="bi
                                                           bi-credit-card me-2">
                                                </i>

                                                Thanh toán Online

                                            </button>
                                          `
                                        : `
                                            <button
                                                type="button"
                                                class="btn btn-light"
                                                disabled>

                                                <i
                                                    class="bi
                                                           bi-check-circle me-2">
                                                </i>

                                                Đã thanh toán

                                            </button>
                                          `
                                }

                            </div>

                        </div>
                    `;

                }
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


    button.disabled = true;


    const originalText =
        button.innerHTML;


    button.innerHTML = `
        <span
            class="spinner-border
                   spinner-border-sm
                   me-2">
        </span>

        Đang thanh toán...
    `;


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

            let message =
                "Thanh toán thất bại.";


            if (
                typeof data ===
                "object"
            ) {

                if (
                    Array.isArray(
                        data.detail
                    )
                ) {

                    message =
                        data.detail
                            .map(
                                item =>
                                    item.msg
                            )
                            .join(
                                "; "
                            );

                }
                else if (
                    data.detail
                ) {

                    message =
                        data.detail;

                }

            }


            showInvoiceAlert(
                message,
                "danger"
            );


            button.disabled = false;

            button.innerHTML =
                originalText;

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


        button.disabled = false;

        button.innerHTML =
            originalText;

    }

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