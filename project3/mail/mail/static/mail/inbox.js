document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // send email on form submit
  document.querySelector('#compose-form').onsubmit = () => {
    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;
    send_mail(recipients, subject, body)
    
    // load sent mail
    .then(() => load_mailbox('sent'));
    
    return false;
  }
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // Show mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    const div = document.createElement('ul');
    div.classList.add('list-group');
    for (let i in emails ) {
      let li = document.createElement('li');
      li.classList.add('list-group-item');
      li.innerHTML = `
        <strong>From: ${emails[i].sender}</strong>
        ${emails[i].timestamp}
        <div>Subject: ${emails[i].subject}</div>
      `;
      

      // view email on click
      li.addEventListener('click', function() {
        view_email(emails[i].id, mailbox)
      });


      // determine background color 
      if (emails[i].read === false) {
        li.style.background = 'white';
      } else {
        li.style.background = 'grey';
      }
      div.appendChild(li);
    }
    document.querySelector('#emails-view').append(div);
  });
}

function send_mail(recipients, subject, body) {
  return fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject,
      body: body
    })
  })
  .then(response => response.json())
  .then(result => {
    console.log(result);
  });
}

function view_email(email_id, mailbox) {
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    document.querySelector('#emails-view').innerHTML = `
      <strong>From: ${email.sender}</strong>
      ${email.timestamp}
      <div>Recipients: ${email.recipients}</div>
      <div>Subject: ${email.subject}</div>
      <hr>
      <div>${email.body}</div>
    `;

    // mark email as read
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    })
    
    // add buttons depending on mailbox
    if (mailbox === 'inbox') {
      // add archive button
      const button = document.createElement('button');
      button.setAttribute("class", "btn btn-danger");
      button.innerHTML = 'Archive';
      button.addEventListener('click', function() {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: true
          })
        })
        .then(() => load_mailbox('inbox'))
      });
      document.querySelector('#emails-view').append(button);

      // add reply button
      const replyButton = document.createElement('button');
      replyButton.setAttribute("class", "btn btn-primary");
      replyButton.innerHTML = 'Reply';
      replyButton.addEventListener('click', function() {
        compose_email()
        document.querySelector('#compose-recipients').value = `${email.recipients}`;
        document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
        document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
      });
      document.querySelector('#emails-view').append(replyButton);
    
    } else if (mailbox === 'archive') {
      // add unarchive button
      const button = document.createElement('button');
      button.setAttribute("class", "btn btn-primary");
      button.innerHTML = 'Unarchive';
      button.addEventListener('click', function() {
        fetch(`/emails/${email_id}`, {
          method: 'PUT',
          body: JSON.stringify({
            archived: false
          })
        })
        .then(() => load_mailbox('inbox'))
      });
      document.querySelector('#emails-view').append(button);
    }

  })
}