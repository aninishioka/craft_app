def removeFieldListEntry(list):
    """Takes WTForm FormField with FieldList type and index. Removes entry
    at index from list."""

    keep = [entry.data for entry in list.entries if not entry.delete.data]

    init_list_size = len(list)

    for entry in range(init_list_size):
        list.pop_entry()

    for entry in keep:
        list.append_entry(entry)

    return len(list) != init_list_size


def prepopulateFormFieldList(field_list, data_list):

    pass
