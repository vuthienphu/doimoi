============================
Ahkio Helpdesk Project Sync
============================

Overview
========

This module enhances the synchronization between Helpdesk tickets and Project tasks,
providing **bidirectional conversion** (ticket ↔ task), **bidirectional chatter
synchronization**, and improved workflow management with flexible archiving options.

Features
========

Bidirectional Conversion
-------------------------

* **Ticket to Task**: Convert helpdesk tickets into project tasks using the
  **Convert to Task** button on the ticket form or the gear (action) menu
* **Task to Ticket**: Convert project tasks into helpdesk tickets using the
  **Convert to Ticket** button on the task form or the gear (action) menu
* **Optional Archiving**: Choose whether to archive the source record after conversion
* **Circular Prevention**: Prevents converting records that were already converted
  from the other type (e.g., cannot convert a task back to a ticket if it was
  originally created from a ticket)
* **Historical Message Sync**: Existing thread messages are automatically copied
  to the newly created record at conversion time
* **Tag Copying**: Tags are copied to the converted record by matching tag names
  across models (``helpdesk.tag`` ↔ ``project.tags``); tags with no name match
  in the target model are silently skipped

Bidirectional Chatter Sync
---------------------------

* **Automatic Message Synchronization**: Messages posted in the ticket chatter are
  automatically synced to all linked tasks, and vice versa
* **Original Formatting Preserved**: Synced messages retain their original message type
  (emails appear as emails, internal notes as notes, etc.)
* **Clickable References**: Synced messages include clickable links to the source
  record (ticket or task) for easy navigation
* **No Duplicate Notifications**: Synced messages do not trigger outgoing emails or
  inbox notifications, preventing notification spam
* **Attachment Sync**: Attachments are duplicated with correct ownership on the target
  record, ensuring all users with access to the target can open them
* **Reaction Sync**: Emoji reactions by internal users (partners) are copied to the
  synced message; guest reactions are skipped
* **Smart Filtering**: System notifications are excluded from syncing to avoid clutter
* **Unified Sync Target**: Messages sync to all related records simultaneously —
  the source record (if converted from another), any records converted from this
  one, and all manually linked records

Ticket-Task Linking
--------------------

**Ticket Links:**

* **Original Task Reference**: Field ``project_task_id`` tracks the task a ticket
  was converted from
* **Converted Tasks**: Field ``task_ids`` tracks all tasks created from this ticket
* **Linked Tasks**: Field ``linked_task_ids`` shows all related tasks in one place —
  converted tasks are added automatically on conversion, and additional existing tasks
  can be linked manually; filtered to tasks belonging to projects with the same customer
* **Smart Button**: Displays the combined count of all related tasks with quick access

**Task Links:**

* **Original Ticket Reference**: Field ``helpdesk_ticket_id`` tracks the ticket a task
  was converted from
* **Converted Tickets**: Field ``ticket_ids`` tracks all tickets created from this task
* **Linked Tickets**: Field ``linked_ticket_ids`` shows all related tickets in one place —
  converted tickets are added automatically on conversion, and additional existing tickets
  can be linked manually; filtered to tickets with the same customer
* **Smart Button**: Displays the combined count of all related tickets with quick access

Archive Control
---------------

* **Optional Archiving on Conversion**: When converting either direction, users can
  choose whether to archive the source record or keep it active
* **Flexible Workflow**: Supports workflows where the original record remains active
  for tracking even after conversion

Usage
=====

Converting Tickets to Tasks
----------------------------

1. Open a Helpdesk ticket
2. Click the **Convert to Task** button in the form header, or use the gear
   (action) menu and select *Convert to Task*
3. Select the target project and stage
4. **Check or uncheck "Archive Ticket"** based on your workflow:

   * **Checked**: Ticket will be archived after conversion
   * **Unchecked**: Ticket remains active and linked to the task

5. Click **Convert**

The created task will maintain a permanent link to the original ticket.
The ticket appears in the task's **Linked Tickets** field, and the task appears
in the ticket's **Linked Tasks** field.
Existing messages from the ticket thread are automatically copied to the new task.

**Note**: Tickets that were converted from tasks cannot be converted back to tasks
to prevent circular conversion chains.

Converting Tasks to Tickets
----------------------------

1. Open a Project task
2. Click the **Convert to Ticket** button in the form header, or use the gear
   (action) menu and select *Convert to Ticket*
3. Select the target helpdesk team and stage
4. **Check or uncheck "Archive Task"** based on your workflow:

   * **Checked**: Task will be archived after conversion
   * **Unchecked**: Task remains active and linked to the ticket

5. Click **Convert**

The created ticket will maintain a permanent link to the original task.
The task appears in the ticket's **Linked Tasks** field, and the ticket appears
in the task's **Linked Tickets** field.
Existing messages from the task thread are automatically copied to the new ticket.

**Note**: Tasks that were converted from tickets cannot be converted back to tickets
to prevent circular conversion chains.

Linking Existing Tasks to Tickets
----------------------------------

1. Open a Helpdesk ticket
2. Use the **Linked Tasks** field to search for and select additional project tasks
3. Only tasks with the same customer are shown; tasks already linked or converted are excluded
4. Messages posted on the ticket will be synced to all linked tasks, and vice versa
5. The **Tasks** smart button counter includes both converted and linked tasks

Linking Existing Tickets to Tasks
----------------------------------

1. Open a Project task
2. Use the **Linked Tickets** field to search for and select additional helpdesk tickets
3. Only tickets with the same customer are shown; tickets already linked or converted are excluded
4. Messages posted on the task will be synced to all linked tickets, and vice versa
5. The **Tickets** smart button counter includes both converted and linked tickets

Syncing Messages
----------------

Messages sync automatically between tickets and tasks based on their relationships:

1. Post a message (comment, note, or email) in either the ticket or task chatter
2. The message automatically appears in the linked record(s) with:

   * A small header indicating it was synced from the other record
   * A clickable link to view the source record
   * All original attachments

Messages sync to **all related records simultaneously** — the source record (if this
record was converted from another), records converted from this one, and all manually
linked records.

**Note**: Synced messages are visible to all users with access to the target record
but do not send outgoing emails or inbox notifications to followers.

Viewing Linked Records
----------------------

**From a Ticket:**

* Click the **Tasks** smart button to view all linked tasks
* Shows the original task (if ticket was converted from a task) OR converted tasks
* Opens a single task directly or a list view if multiple tasks exist

**From a Task:**

* Click the **Tickets** smart button to view all linked tickets
* Shows the original ticket (if task was converted from a ticket) OR converted tickets
* Opens a single ticket directly or a list view if multiple tickets exist

Technical Details
=================

Database Structure
------------------

**helpdesk.ticket:**

* ``project_task_id`` (Many2one to project.task): References the task this ticket
  was converted from
* ``task_ids`` (One2many to project.task): References all tasks converted from
  this ticket
* ``linked_task_ids`` (Many2many to project.task, via ``helpdesk_ticket_linked_task_rel``):
  All related tasks — populated automatically on conversion and supplemented by manual
  links; filtered by projects with the same customer
* ``linked_task_ids_domain`` (Char, computed): Serialised Python list (``str(domain)``)
  used as the widget domain for ``linked_task_ids`` in the view; excludes ``task_ids``,
  current ``linked_task_ids``, and ``project_task_id`` to prevent duplicates

**project.task:**

* ``helpdesk_ticket_id`` (Many2one to helpdesk.ticket): References the ticket this
  task was converted from
* ``ticket_ids`` (One2many to helpdesk.ticket): References all tickets converted
  from this task
* ``linked_ticket_ids`` (Many2many to helpdesk.ticket, via ``helpdesk_ticket_linked_task_rel``):
  All related tickets — populated automatically on conversion and supplemented by manual
  links; filtered to tickets with the same customer
* ``linked_ticket_ids_domain`` (Char, computed): Serialised Python list (``str(domain)``)
  used as the widget domain for ``linked_ticket_ids`` in the view; excludes ``ticket_ids``,
  current ``linked_ticket_ids``, and ``helpdesk_ticket_id`` to prevent duplicates

All Many2one fields use btree_not_null indexes for performance.

Message Sync Implementation
---------------------------

* Uses ``_message_post_after_hook`` override on both models
* Synced messages are created via ``mail.message.copy()``, which:

  * Preserves the original message type, author, and formatting
  * Never triggers outgoing email or inbox notifications (``mail.notification`` and
    ``mail.mail`` records have ``copy=False`` in core)
  * Bypasses ``_message_post_after_hook`` entirely, so no infinite sync loop is possible

* Attachments are duplicated via ``ir.attachment.copy()`` with the target record's
  ``res_model``/``res_id``, ensuring correct access-rights enforcement
* Emoji reactions (``mail.message.reaction``) by partners are re-created on the synced
  message; guest reactions (``guest_id``-only) are skipped as they cannot be
  re-attributed without an active guest session
* The sync header ("Message synced from …") is prepended using ``markupsafe.Markup``
* Sync target is the union of all three relationship fields —
  ``project_task_id | task_ids | linked_task_ids`` (ticket side) and
  ``helpdesk_ticket_id | ticket_ids | linked_ticket_ids`` (task side); Odoo recordset
  ``|`` deduplicates automatically, so records that appear in more than one field
  (e.g. a converted task that is also in ``linked_task_ids``) receive only one copy

Historical Message Sync on Conversion
--------------------------------------

* Implemented in ``HelpdeskTicketConvertWizard._sync_thread_messages_to_tasks`` and
  ``ProjectTaskConvertWizard._sync_thread_messages_to_tickets``
* On conversion, existing non-notification messages from the source thread are copied
  to the new record in chronological order, sorted by ``(date, id)``
* Reactions and attachments are copied using the same logic as live chatter sync
* Tags are copied by matching names across models (``helpdesk.tag`` ↔
  ``project.tags``); unmatched tags are silently skipped
* The converted record is added to the source's ``linked_task_ids`` /
  ``linked_ticket_ids``, and the source is back-linked into the new record's
  corresponding linked field, so both sides see each other immediately in the
  linked field without any manual linking step

Circular Conversion Prevention
-------------------------------

* ``action_convert_to_ticket()`` override validates tasks don't have ``helpdesk_ticket_id``
* ``action_convert_to_task()`` override validates tickets don't have ``project_task_id``
* Shows user-friendly warning notifications when conversion is blocked
* Allows fresh records and records with children to be converted normally

Tests
=====

The module ships with an automated test suite. All tests
live under the ``tests/`` directory and share a common base class
(``HelpdeskProjectSyncCommon``) that provides reusable fixtures and helpers.

Conversion (``tests/test_conversion.py``)
------------------------------------------

``TestConversionWizard`` covers both conversion directions:

**Ticket → Task**

* Field mapping (project, stage, partner, ``helpdesk_ticket_id``)
* Optional archiving: ``archive_ticket`` defaults to ``False``; setting it to ``True``
  archives the source ticket
* Historical message copying: non-notification messages are copied; notifications are
  excluded
* Attachment ownership: copied attachments have ``res_model='project.task'``
* Batch conversion of multiple tickets returns a list-view action
* Circular-conversion prevention returns a warning notification

**Task → Ticket**

* Same coverage in the reverse direction (team, stage, partner, ``project_task_id``,
  ``archive_task``, historical messages, attachment ownership, batch conversion, and
  circular-conversion prevention)

Chatter Synchronisation (``tests/test_chatter_sync.py``)
----------------------------------------------------------

``TestChatterSync`` verifies bidirectional live sync:

* Messages sync from ticket to all related tasks simultaneously — union of
  ``project_task_id``, ``task_ids``, and ``linked_task_ids``
* Notification messages are **not** synced
* Message type is preserved in the synced copy
* Synced message body contains a clickable ``data-oe`` link back to the source record
* Attachments are duplicated with the target record as owner
* No sync loop: posting on one side does not echo a message back

The same suite covers the task → ticket direction symmetrically.

Manual Linking (``tests/test_linking.py``)
-------------------------------------------

``TestManualLinking`` and ``TestSmartButtonCounts`` cover:

* Creating and reading many-to-many links in both directions
* Bidirectional M2M consistency (linking from one side is visible on both)
* Domain filtering: partner-based filter applied only when a partner is set;
  exclusion of already-linked and already-converted records; domain fields are
  stored as serialised strings and tests parse them with ``ast.literal_eval``
* Smart button counts (``task_ids_count`` / ``ticket_ids_count``) correctly include
  both converted and linked records without double-counting

Credits
=======

Authors
-------

* Ahkio Consulting Oy
