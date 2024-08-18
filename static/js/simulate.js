Chart.defaults.color = '#FFFFFC80'
Chart.defaults.font.size = '24'
Chart.defaults.backgroundColor = '#FFFFFC'
Chart.defaults.borderColor = '#FFFFFC30'

async function loadData() {
    
    const sim_response = await fetch('/retrieve-sim-data');
    console.log('Sim response: ', sim_response);
    
    const data = await sim_response.json();
    console.log('Data: ', data);

    const loan_response = await fetch('/retrieve-loans');
    console.log('Loan response: ', loan_response);

    const loan_list = await loan_response.json();
    console.log('Loan list: ', loan_list)

    const ctx = document.getElementById('simulate-payments-chart');

    const mapped_data = getData(data);
    console.log('Mapped data: ', mapped_data);

    const dataSet = createDataset(loan_list, mapped_data);
    console.log('Dataset: ', dataSet);


    const cfg = {
        type: 'line',
        data: {
          datasets: createDataset(loan_list, mapped_data)
        },
        options: {
            scales: {
                x: {
                    position: 'bottom',
                },
                y: {
                    ticks: {
                        // Include a dollar sign in the ticks
                        callback: function(value, index, ticks) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    }
      

    new Chart(ctx, cfg);


    // new Chart(
    //     document.getElementById('acquisitions'),
    //     {
    //       type: 'bar',
    //       data: {
    //         labels: data.map(row => row.year),
    //         datasets: [
    //           {
    //             label: 'Acquisitions by year',
    //             data: data.map(row => row.count)
    //           }
    //         ]
    //       }
    //     }
    //   );
    };
      

function getData(dict) {
    let array = Object.entries(dict);
    console.log(array);
    let data = [];
    for (let payment = 0; payment < array.length; payment++) {
        console.log(array[payment][1]);
        data.push(array[payment][1]);
    }
    console.log(data);
    
    console.log("Finished loop");
    // for (let payment = 0; payment < length(dict))
    return data
}

function createDataset(loan_list, mapped_data) {
    let dataset = [];
    for (let i = 0; i < loan_list.length; i++) {
        console.log(loan_list[i])
        dataset.push({
            label: loan_list[i],
            data: mapped_data
            .filter(row => row.label == loan_list[i])
            .map(row => ({
                x: row.date,
                y: row.balance
            }))
        });
    };

    return dataset
}


loadData();
