document.addEventListener("DOMContentLoaded", function () {
    console.log("confirm.js is running...");

    window.downloadReceipt = function () {
        console.log("Download button clicked.");

        const element = document.getElementById("confirmation-container");
        if (!element) {
            console.error("Error: confirmation-container not found!");
            return;
        }

        html2canvas(element, { scale: 2 }).then((canvas) => {
            console.log("Canvas generated.");
            const imgData = canvas.toDataURL("image/png");
            const pdf = new jspdf.jsPDF("p", "mm", "a4");

            const imgWidth = 210; // A4 width in mm
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            pdf.addImage(imgData, "PNG", 0, 10, imgWidth, imgHeight);
            pdf.save("order_receipt.pdf");
            console.log("PDF saved successfully.");
        }).catch((error) => {
            console.error("Error generating PDF:", error);
        });
    };
});
