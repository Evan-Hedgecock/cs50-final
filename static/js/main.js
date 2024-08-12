function myFunction() {
    console.log("Function running");
}

myFunction();

function dropDown() {
    document.getElementById("profile-dropdown").classList.toggle("show");
    document.getElementById("profile-button").classList.toggle("ignore");
    }

function toggleSidebar() {
    document.getElementById('s-m').classList.toggle('visible');
    document.getElementById('s-m').classList.toggle('collapse');
    }

function openAddForm() {
    document.getElementById('add-loan-form-container').classList.toggle('visible');
    document.getElementById('add-loan-form-container').classList.toggle('collapse');
    toggleSidebar()

    }

function openEditForm() {
    document.getElementById('edit-loan-form-container').classList.toggle('visible');
    document.getElementById('edit-loan-form-container').classList.toggle('collapse');
    toggleSidebar()
}

function openPaymentForm() {
    document.getElementById('make-payment-form-container').classList.toggle('visible');
    document.getElementById('make-payment-form-container').classList.toggle('collapse');
    toggleSidebar()
}

function goBack(openForm) {
    openForm
}

function onlyNumberKey(evt) {
    // Only ASCII character in that range allowed
    var ASCIICode = (evt.which) ? evt.which : evt.keyCode
    console.log(ASCIICode)
    if ((ASCIICode <= 57 && ASCIICode >= 48) || ASCIICode == 46) {
        return true;
    }
    else {
        return false;
    }
}

function formatToUSD(value) {
    let number = parseFloat(value);
    if (isNaN(number)) {
        return "";
    }
    // Format number with commas and two decimal places
    return "$" + number.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatToPercentage(value) {
    let number = parseFloat(value);
    if (isNaN(number)) {
        return "";
    }
    // Format number to two decimal places with percent sign
    return number.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + "%";
}

function formatInput(event) {
    const input = event.target;
    const value = input.value.replace(/,/g, ''); // Remove commas for proper formatting
    const formatType = input.dataset.format; // Determine format type using data attribute

    let formattedValue;
    if (formatType === "usd") {
        formattedValue = formatToUSD(value);
    } else if (formatType === "percentage") {
        formattedValue = formatToPercentage(value);
    }

    // Find the corresponding <span> element to update
    const formattedSpan = input.nextElementSibling;
    formattedSpan.innerText = formattedValue;
}

function displayFlashedMessages(messages, formName) {
    console.log("When flashed, formName =", formName);
    
    const container = document.getElementById("flashed-messages-container");
    messages.forEach(([category, message]) => {
        console.log("Message: " + message + "\n" + "Category: " + category);
        
        const messageElement = document.createElement("div");
        messageElement.className = `flashes ${category}`;
        messageElement.innerText = message;
        container.appendChild(messageElement);

        // Position the message relative to the form
        const form = document.getElementById(formName);
        form.parentNode.insertBefore(container, form); // Insert the container before the form
        console.log("Form name: " + formName)
        const formRect = form.getBoundingClientRect();
        console.log(formRect);
        console.log("formRect width: " + (formRect.width / 2) )
        
        messageElement.style.bottom = formRect.top + 'px';
        messageElement.style.left = formRect.left + 'px'; 
        messageElement.style.width = formRect.width + 'px';
        console.log("messageElement width: " + messageElement.getBoundingClientRect().width)
    });
}

function setSelectedOptionId(dropdown_id) {
    var dropDown = document.getElementById(dropdown_id);
    console.log("dropdown:", dropDown);
    
    var selectedOption = dropDown.options[dropDown.selectedIndex];
    console.log("selected option:", selectedOption);
    
    var hiddenInput = document.getElementById("selected-option-id");
    console.log("hidden input:", hiddenInput);
    
    hiddenInput.value = selectedOption.id;
    console.log("hidden value:", hiddenInput.value);
    
}