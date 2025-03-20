const client = new Typesense.Client({
  nodes: [{
    host: '0.0.0.0',
    port: '8108',
    protocol: 'http'
  }],
  apiKey: 'CHANGE_API_KEY',
  connectionTimeoutSeconds: 2
});

let currentPage = 1;

document.getElementById('search-box').addEventListener('input', debounce(search, 300));
document.getElementById('source-filter').addEventListener('change', search);
document.getElementById('results-per-page').addEventListener('change', search);

function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

async function search() {
  const query = document.getElementById('search-box').value;
  const sourceFilter = document.getElementById('source-filter').value;
  const perPage = parseInt(document.getElementById('results-per-page').value) || 10;

  if (query.length === 0) {
    document.getElementById('results').innerHTML = '';
    document.getElementById('pagination').innerHTML = '';
    return;
  }

  const searchParameters = {
    q: query,
    query_by: 'ocr_text_original',
    per_page: perPage,
    page: currentPage,
    highlight_full_fields: 'ocr_text_original',
    sort_by: '_text_match:desc'
  };

  if (sourceFilter) {
    searchParameters.filter_by = `source:${sourceFilter}`;
  }

  try {
    const searchResults = await client.collections('documents').documents().search(searchParameters);
    displayResults(searchResults);
    displayPagination(searchResults.found, perPage);
  } catch (error) {
    console.error('Search error:', error);
  }
}

function displayResults(results) {
  const resultsContainer = document.getElementById('results');
  resultsContainer.innerHTML = '';

  if (results.hits.length === 0) {
    resultsContainer.innerHTML = '<div class="notification is-info">No results found</div>';
    return;
  }

  results.hits.forEach(result => {
    const card = document.createElement('div');
    card.className = 'card';

    const cardContent = document.createElement('div');
    cardContent.className = 'card-content';

    const titleContainer = document.createElement('div');
    titleContainer.className = 'is-flex is-justify-content-space-between is-align-items-center';

    const title = document.createElement('p');
    title.className = 'title is-4';
    title.textContent = `Page ${result.document.page_number}`;

    const sourceTag = document.createElement('span');
    sourceTag.className = 'tag is-info source-tag';
    sourceTag.textContent = result.document.source;

    titleContainer.appendChild(title);
    titleContainer.appendChild(sourceTag);

    const snippet = document.createElement('div');
    snippet.className = 'content';
    snippet.innerHTML = result.highlights[0].snippet;

    const actions = document.createElement('div');
    actions.className = 'field is-grouped mt-4';

    const viewButton = document.createElement('p');
    viewButton.className = 'control';
    viewButton.innerHTML = `<a href="${result.document.remote_path}" target="_blank" class="button is-link">View Original</a>`;

    const imageButton = document.createElement('p');
    imageButton.className = 'control';
    imageButton.innerHTML = `<a href="${result.document.image_url}" target="_blank" class="button is-link is-light">View Image</a>`;

    actions.appendChild(viewButton);
    actions.appendChild(imageButton);

    cardContent.appendChild(titleContainer);
    cardContent.appendChild(snippet);
    cardContent.appendChild(actions);
    card.appendChild(cardContent);
    resultsContainer.appendChild(card);
  });
}

function displayPagination(total, perPage) {
  const totalPages = Math.ceil(total / perPage);
  const pagination = document.getElementById('pagination');
  pagination.innerHTML = '';

  if (totalPages <= 1) return;

  const nav = document.createElement('nav');
  nav.className = 'pagination';

  const previousButton = document.createElement('a');
  previousButton.className = `pagination-previous ${currentPage === 1 ? 'is-disabled' : ''}`;
  previousButton.textContent = 'Previous';
  previousButton.onclick = () => {
    if (currentPage > 1) {
      currentPage--;
      search();
    }
  };

  const nextButton = document.createElement('a');
  nextButton.className = `pagination-next ${currentPage === totalPages ? 'is-disabled' : ''}`;
  nextButton.textContent = 'Next';
  nextButton.onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;
      search();
    }
  };

  nav.appendChild(previousButton);
  nav.appendChild(nextButton);
  pagination.appendChild(nav);
}
