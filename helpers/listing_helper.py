# Remove and then publish each listing
def update_listings(listings, type, scraper):
	# If listings are empty stop the function
	if not listings:
		return

	# Check if listing is already listed and remove it then publish it like a new one
	for listing in listings:
		# Remove listing if it is already published
		remove_listing(listing, type, scraper)

		# Publish the listing in marketplace
		isPublished = publish_listing(listing, type, scraper)

		# If the listing is not published from the first time, try again
		if not isPublished:
			publish_listing(listing, type, scraper)

def remove_listing(data, listing_type, scraper) :
	title = generate_title_for_listing_type(data, listing_type)
	listing_title = find_listing_by_title(title, scraper)
	# Listing not found so stop the function
	if not listing_title:
		return

	listing_title.click()

	# Click on the delete listing button
	scraper.element_click('div:not([role="gridcell"]) > div[aria-label="Delete"][tabindex="0"]')

	# Click on confirm button to delete
	confirm_delete_selector = 'div[aria-hidden="false"] div[aria-label="Delete"][tabindex="0"]'
	if scraper.find_element(confirm_delete_selector, False, 3):
		scraper.element_click(confirm_delete_selector)
	else:
		confirm_delete_selector = 'div[aria-hidden="false"] div[aria-label="Delete"][tabindex="0"]'
		if scraper.find_element(confirm_delete_selector, True, 3):
			scraper.element_click(confirm_delete_selector)
	
	# Wait until the popup is closed
	scraper.element_wait_to_be_invisible('div[aria-label="Your Listing"]')

def publish_listing(data, listing_type, scraper):
	create_listing_button_selector = 'div[aria-label="Marketplace sidebar"] a[aria-label="Create new listing"]'
	create_listing_button = scraper.find_element(create_listing_button_selector, False, 20)

	if create_listing_button:
		# Click on create new listing button
		scraper.element_click(create_listing_button_selector)
	else:
		# Refresh marketplace selling page
		scraper.go_to_page('https://facebook.com/marketplace/you/selling')
		scraper.element_click(create_listing_button_selector)

	# Choose listing type
	#scraper.element_click('a[href="/marketplace/create/' + listing_type + '/"]')
	scraper.element_click_by_xpath('//span[text()="Item for sale"]')
	# Create string that contains all of the image paths separeted by \n
	images_path = generate_multiple_images_path(data['Photos Folder'], data['Photos Names'])
	# Add images to the the listing
	scraper.input_file_add_files('input[accept="image/*,image/heif,image/heic"]', images_path)

	# Add specific fields based on the listing_type
	function_name = 'add_fields_for_' + listing_type
	# Call function by name dynamically
	globals()[function_name](data, scraper)
	
	scraper.element_send_keys_by_xpath('//span[text()="Price"]/following-sibling::input[1]', data['Price'])
	scraper.element_send_keys_by_xpath('//span[text()="Description"]/following-sibling::div/textarea', data['Description'])
	scraper.element_send_keys_by_xpath('//span[text()="Location"]/following-sibling::input[1]', data['Location'])
	scraper.element_click('ul[role="listbox"] li:first-child > div')

	next_button_selector = 'div [aria-label="Next"] > div'
	next_button = scraper.find_element(next_button_selector, False, 3)
	if next_button:
		# Go to the next step
		scraper.element_click(next_button_selector)
		# Add listing to multiple groups
		add_listing_to_multiple_groups(data, scraper)
	
	close_button_selector = '//span[text()="Close"]'
	close_button = scraper.find_element_by_xpath(close_button_selector, False, 10)
	if close_button:
		scraper.element_click_by_xpath(close_button_selector)
		scraper.go_to_page('https://facebook.com/marketplace/you/selling')
		return False

	# Publish the listing
	scraper.element_click('div[aria-label="Publish"]:not([aria-disabled])')

	leave_page_selector = '//div[@tabindex="0"] //span[text()="Leave Page"]'
	leave_page = scraper.find_element_by_xpath(leave_page_selector, False, 15)
	if leave_page:
		scraper.element_click_by_xpath(leave_page_selector)

	# Wait until the listing is published
	wait_until_listing_is_published(listing_type, scraper)

	if not next_button:
		post_listing_to_multiple_groups(data, listing_type, scraper)
	
	return True


def generate_multiple_images_path(path, images):
	# Last character must be '/' because after that we are adding the name of the image
	if path[-1] != '/':
		path += '/'

	images_path = ''

	# Split image names into array by this symbol ";"
	image_names = images.split(';')

	# Create string that contains all of the image paths separeted by \n
	if image_names:
		for image_name in image_names:
			# Remove whitespace before and after the string
			image_name = image_name.strip()

			# Add "\n" for indicating new file
			if images_path != '':
				images_path += '\n'

			images_path += path + image_name

	return images_path

# Add specific fields for listing from type vehicle
def add_fields_for_vehicle(data, scraper):
	# Expand vehicle type select
	scraper.element_click_by_xpath('//span[text()="Vehicle type"]')
	# Select vehicle type
	scraper.element_click_by_xpath('//span[text()="' + data['Vehicle Type'] + '"]')

	# Scroll to years select
	scraper.scroll_to_element_by_xpath('//span[text()="Year"]')
	# Expand years select
	scraper.element_click_by_xpath('//span[text()="Year"]')
	scraper.element_click_by_xpath('//span[text()="' + data['Year'] + '"]')

	scraper.element_send_keys_by_xpath('//span[text()="Make"]/following-sibling::input[1]', data['Make'])
	scraper.element_send_keys_by_xpath('//span[text()="Model"]/following-sibling::input[1]', data['Model'])

	# Scroll to mileage input
	scraper.scroll_to_element_by_xpath('//span[text()="Mileage"]/following-sibling::input[1]')	
	# Click on the mileage input
	scraper.element_send_keys_by_xpath('//span[text()="Mileage"]/following-sibling::input[1]', data['Mileage'])

	# Expand fuel type select
	scraper.element_click_by_xpath('//span[text()="Fuel type"]')
	# Select fuel type
	scraper.element_click_by_xpath('//span[text()="' + data['Fuel Type'] + '"]')

# Add specific fields for listing from type item
def add_fields_for_item(data, scraper):
	scraper.element_send_keys_by_xpath('//span[text()="Title"]/following-sibling::input[1]', data['Title'])

	# Scroll to "Category" select field
	scraper.scroll_to_element_by_xpath('//span[text()="Category"]')
	# Expand category select
	scraper.element_click_by_xpath('//span[text()="Category"]')
	# Select category
	scraper.element_click_by_xpath('//span[text()="' + data['Category'] + '"]')

	# Expand category select
	scraper.element_click_by_xpath('//div/span[text()="Condition"]')
	# Select category
	scraper.element_click_by_xpath('//span[@dir="auto"][text()="' + data['Condition'] + '"]')

	if data['Category'] == 'Sports & Outdoors':
		scraper.element_send_keys_by_xpath('//span[text()="Brand"]/following-sibling::input[1]', data['Brand'])

def generate_title_for_listing_type(data, listing_type):
	title = ''

	if listing_type == 'item':
		title = data['Title']

	if listing_type == 'vehicle':
		title = data['Year'] + ' ' + data['Make'] + ' ' + data['Model']

	return title

def add_listing_to_multiple_groups(data, scraper):
	# Create an array for group names by spliting the string by this symbol ";"
	group_names = data['Groups'].split(';')
	# Clean the array of empty strings.
	group_names = [name for name in group_names if name.strip()]
	# If the groups are empty do not do nothing
	if not group_names or group_names == "''":
		return

	# Post in different groups
	for group_name in group_names:
		# Remove whitespace before and after the name
		group_name = group_name.strip()

		scraper.element_click_by_xpath('//span[text()="' + group_name + '"]')

def post_listing_to_multiple_groups(data, listing_type, scraper):
	title = generate_title_for_listing_type(data, listing_type)
	title_element = find_listing_by_title(title, scraper)

	# If there is no add with this title do not do nothing
	if not title_element:
		return

	# Create an array for group names by spliting the string by this symbol ";"
	group_names = data['Groups'].split(';')

	# If the groups are empty do not do nothing
	if not group_names:
		return

	search_input_selector = '[aria-label="Search for groups"]'

	# Post in different groups
	for group_name in group_names:
		# Click on the Share button to the listing that we want to share
		scraper.element_click_by_xpath('//*[contains(@aria-label, "' + title + '")]//span//span[contains(., "Share")]')
		
		# Click on the Share to a group button
		scraper.element_click_by_xpath('//span[text()="Group"]')

		# Remove whitespace before and after the name
		group_name = group_name.strip()

		# Remove current text from this input
		scraper.element_delete_text(search_input_selector)
		# Enter the title of the group in the input for search
		scraper.element_send_keys(search_input_selector, group_name[:51])
	
		scraper.element_click_by_xpath('//span[text()="' + group_name + '"]')
		
		if (scraper.find_element('[aria-label="Create a public post…"]', False, 3)):
			scraper.element_send_keys('[aria-label="Create a public post…"]', data['Description'])
		elif (scraper.find_element('[aria-label="Write something..."]', False, 3)):
			scraper.element_send_keys('[aria-label="Write something..."]', data['Description'])
		
		scraper.element_click('[aria-label="Post"]:not([aria-disabled])')
		# Wait till the post is posted successfully
		scraper.element_wait_to_be_invisible('[role="dialog"]')
		scraper.element_wait_to_be_invisible('[aria-label="Loading...]"')
		scraper.find_element_by_xpath('//span[text()="Shared to your group."]', False, 10)

def find_listing_by_title(title, scraper):
	searchInput = scraper.find_element('input[placeholder="Search your listings"]', False)
	# Search input field is not existing	
	if not searchInput:
		return False
	
	# Clear input field for searching listings before entering title
	scraper.element_delete_text('input[placeholder="Search your listings"]')
	# Enter the title of the listing in the input for search
	scraper.element_send_keys('input[placeholder="Search your listings"]', title)
	return scraper.find_element_by_xpath('//span[text()="' + title + '"]', False, 10)

def wait_until_listing_is_published(listing_type, scraper):
	if listing_type == 'item':
		scraper.element_wait_to_be_invisible_by_xpath('//h1[text()="Item for sale"]')
	elif listing_type == 'vehicle':
		scraper.element_wait_to_be_invisible_by_xpath('//h1[text()="Vehicle for sale"]')
