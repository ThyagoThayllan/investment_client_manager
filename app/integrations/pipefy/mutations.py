# https://api-docs.pipefy.com/reference/mutations/createCard/
CREATE_CARD_MUTATION: str = '''
    mutation CreateCard($input: CreateCardInput!) {
        createCard(input: $input) {
            card {
                id
                title
            }
        }
    }
'''

# https://api-docs.pipefy.com/reference/mutations/updateFieldsValues/
UPDATE_CARD_FIELDS_MUTATION: str = '''
    mutation UpdateFieldsValues($input: UpdateFieldsValuesInput!) {
        updateFieldsValues(input: $input) {
            success
        }
    }
'''
