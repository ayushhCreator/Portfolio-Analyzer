// Portfolio Analyzer JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize portfolio chart
    loadPortfolioChart();
    
    // Initialize XIRR data when tab is clicked
    document.getElementById('xirr-tab').addEventListener('click', function() {
        loadXIRRData();
    });
    
    // Initialize news functionality
    initializeNews();
});

function loadPortfolioChart() {
    fetch('/api/portfolio-chart')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error loading chart data:', data.error);
                return;
            }
            
            const ctx = document.getElementById('portfolioChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Portfolio Value (USD)',
                        data: data.values,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                parser: 'YYYY-MM-DD',
                                tooltipFormat: 'MMM DD, YYYY',
                                displayFormats: {
                                    day: 'MMM DD',
                                    month: 'MMM YYYY'
                                }
                            }
                        },
                        y: {
                            beginAtZero: false,
                            ticks: {
                                callback: function(value) {
                                    return '$' + value.toLocaleString();
                                }
                            }
                        }
                    },
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return 'Portfolio Value: $' + context.parsed.y.toLocaleString();
                                }
                            }
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error loading portfolio chart:', error);
        });
}

function loadXIRRData() {
    const xirrTable = document.getElementById('xirrTable');
    xirrTable.innerHTML = 'Loading XIRR data...';
    
    fetch('/api/xirr')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                xirrTable.innerHTML = '<p class="text-danger">Error loading XIRR data: ' + data.error + '</p>';
                return;
            }
            
            let tableHTML = '<div class="table-responsive"><table class="table table-striped">';
            tableHTML += '<thead><tr><th>Symbol</th><th>XIRR (Annualized Return)</th></tr></thead><tbody>';
            
            data.forEach(item => {
                const xirrClass = item.xirr_value > 0 ? 'text-success' : (item.xirr_value < 0 ? 'text-danger' : '');
                tableHTML += `<tr><td><strong>${item.symbol}</strong></td><td class="${xirrClass}">${item.xirr}</td></tr>`;
            });
            
            tableHTML += '</tbody></table></div>';
            xirrTable.innerHTML = tableHTML;
        })
        .catch(error => {
            xirrTable.innerHTML = '<p class="text-danger">Error loading XIRR data</p>';
            console.error('Error loading XIRR data:', error);
        });
}

function initializeNews() {
    const newsSelect = document.getElementById('newsSymbolSelect');
    const newsContent = document.getElementById('newsContent');
    
    if (newsSelect) {
        newsSelect.addEventListener('change', function() {
            const symbol = this.value;
            if (!symbol) {
                newsContent.innerHTML = 'Select a symbol to view news';
                return;
            }
            
            newsContent.innerHTML = 'Loading news for ' + symbol + '...';
            
            fetch('/api/news/' + symbol)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        newsContent.innerHTML = '<p class="text-danger">Error loading news: ' + data.error + '</p>';
                        return;
                    }
                    
                    let newsHTML = '';
                    data.news.forEach(item => {
                        newsHTML += '<div class="news-item">' + item + '</div>';
                    });
                    
                    newsContent.innerHTML = newsHTML || '<p class="text-muted">No news available for ' + symbol + '</p>';
                })
                .catch(error => {
                    newsContent.innerHTML = '<p class="text-danger">Error loading news</p>';
                    console.error('Error loading news:', error);
                });
        });
    }
}