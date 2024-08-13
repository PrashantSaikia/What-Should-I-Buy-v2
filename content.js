document.addEventListener('DOMContentLoaded', function () {
  var submitButton = document.getElementById('submit-button');
  submitButton.addEventListener('click', function () {
    var categoryInput = document.getElementById('category-input');
    var category = categoryInput.value;
    var loadingIcon = document.getElementById('loading-icon');
    var recommendationsTable = document.getElementById('recommendations-table');
    
    loadingIcon.style.display = 'block';
    recommendationsTable.innerHTML = '';

    fetch(`http://localhost:8050/get_recommendations?category=${category}`)
      .then(response => response.json())
      .then(data => {
        console.log('Fetched data:', data);  // Log the fetched data
        var tableHTML = '<table>';
        for (var i = 0; i < data.length; i++) {
          tableHTML += '<tr>';
          for (var key in data[i]) {
            tableHTML += `<td>${data[i][key]}</td>`;
          }
          tableHTML += '</tr>';
        }
        tableHTML += '</table>';
        recommendationsTable.innerHTML = tableHTML;
        loadingIcon.style.display = 'none';
        window.recommendationsData = data;
        console.log('Data stored in window.recommendationsData');  // Confirm data is stored
      })
      .catch(error => {
        console.error('Error fetching recommendations:', error);
        loadingIcon.style.display = 'none';
      });
  });
  
  document.getElementById('saveButton').addEventListener('click', saveResults);
});

function saveResults() {
  console.log('Saving results...');
  if (!window.recommendationsData || window.recommendationsData.length === 0) {
    alert('No results to save!');
    return;
  }

  var categoryInput = document.getElementById('category-input');
  var category = categoryInput.value.trim();
  var filename = category ? `${category}.json` : 'recommendations.json';

  const jsonData = JSON.stringify(window.recommendationsData, null, 2);
  const blob = new Blob([jsonData], { type: 'application/json' });
  const url = URL.createObjectURL(blob);

  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  console.log('Results saved');
}