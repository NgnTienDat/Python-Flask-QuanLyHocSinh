// Lấy tham chiếu đến canvas
    const ctx = document.getElementById('student-chart').getContext('2d');

    // Dữ liệu số lượng học sinh qua các năm
    const data = {
        labels: ['2018', '2019', '2020', '2021', '2022', '2023'], // Năm học
        datasets: [{
            label: 'Số lượng học sinh',
            data: [150, 200, 250, 300, 350, 400], // Số lượng học sinh mỗi năm
            backgroundColor: 'rgba(54, 162, 235, 0.5)', // Màu cột
            borderColor: 'rgba(54, 162, 235, 1)', // Màu viền
            borderWidth: 1
        }]
    };

    // Cấu hình biểu đồ
    const config = {
        type: 'bar', // Loại biểu đồ: bar (cột)
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Số lượng học sinh qua các năm học'
                }
            },
            scales: {
                y: {
                    beginAtZero: true, // Bắt đầu từ 0
                    title: {
                        display: true,
                        text: 'Số lượng học sinh'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Năm học'
                    }
                }
            }
        }
    };

    // Vẽ biểu đồ
    new Chart(ctx, config);