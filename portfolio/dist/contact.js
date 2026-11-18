const contactForm = document.querySelector("#contact-form");
const contactName = contactForm.elements.namedItem("name");
const contactMessage = contactForm.elements.namedItem("message");
const draftLink = document.querySelector("#contact-email-draft");
const composeResult = document.querySelector("#contact-compose-result");

for (const field of [contactName, contactMessage]) {
  field.addEventListener("input", () => field.setCustomValidity(""));
}

contactForm.addEventListener("submit", (event) => {
  event.preventDefault();
  contactName.setCustomValidity(
    contactName.value.trim() ? "" : "Please enter your name.",
  );
  contactMessage.setCustomValidity(
    contactMessage.value.trim() ? "" : "Please enter your message.",
  );
  if (!contactForm.reportValidity()) return;

  const values = new FormData(contactForm);
  const name = values.get("name").trim();
  const email = values.get("email").trim();
  const phone = values.get("phone").trim();
  const topic = values.get("topic");
  const message = values.get("message").trim().replace(/\r?\n/g, "\r\n");
  const subject = `Portfolio enquiry: ${topic} - ${name}`;
  const body = [
    "Hello Raihan,",
    "",
    message,
    "",
    `Name: ${name}`,
    `Email: ${email}`,
    ...(phone ? [`Phone: ${phone}`] : []),
    `Topic: ${topic}`,
  ].join("\r\n");
  draftLink.href = `mailto:raihanrifaldiii@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  composeResult.hidden = false;
  draftLink.click();
});
