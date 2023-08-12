// Script to clean displayed items based on selected category
// This could be done solely in Flask, but that would result in so many page reloads

// selectors
const categoryItems = document.querySelectorAll('.category-item');
const itemContainer = document.querySelector('.items-list');

// functionality

// fetch and display items based on category
function loadItems(categoryId) {
	fetch(`/get_items_by_category/${categoryId}`)
		.then((response) => response.json())
		.then((data) => {
			// clear previous content
			itemContainer.innerHTML = '';

			// create item element for each item
			// and appending to parent
			data.items.forEach((item) => {
				const itemElement = createItemElement(item);
				itemContainer.appendChild(itemElement);
			});
		});
}

// fetch and display all items (on categories page load pretty much)
function loadAllItems() {
	fetch(`/get_all_items`)
		.then((response) => response.json())
		.then((data) => {
			// clear previous items
			itemContainer.innerHTML = '';

			data.items.forEach((item) => {
				const itemElement = createItemElement(item);
				itemContainer.appendChild(itemElement);
			});
		});
}

// create an item element
function createItemElement(item) {
	// this is similar to the item_card.html template content
	// but we don't have a way of using Jinja2 templates client side
	// without running into some serious security issues
	const itemElement = document.createElement('a');
	itemElement.setAttribute('href', `/items/${item.item_id}`);
	itemElement.innerHTML = `
        <div class="item-card">
            <div class="item-image">
                <img src="/static/imgs/${item.filename}" alt="Product image" />
            </div>
            <div class="item-info">
                <p class="item-name">${item.name}</p>
                <hr />
                <p class="item-price">£${item.price}</p>
            </div>
        </div>
    `;
	return itemElement;
}

// event listeners
categoryItems.forEach((item) => {
	item.addEventListener('click', (event) => {
		// preventing default anchor behaviour
		event.preventDefault();
		// get selected category_id
		const categoryId = item.dataset.categoryId;
		if (categoryId === '-1') {
			loadAllItems();
		} else {
			loadItems(categoryId);
		}
	});
});

document.addEventListener('DOMContentLoaded', loadAllItems);