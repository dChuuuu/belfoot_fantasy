from .custom_exceptions import WrongTableException400, IncompleteDataException400

def collect_data(request, table_name=None):

    if table_name == 'turns':
        try:
            turns_data = {'season': request.data['season'],
                          'url': request.data['url'],
                          'logo': request.data['logo'],
                          'name': request.data['name'],
                          'description': request.data['description'],
                          'categories': request.data['categories'],
                          'type': request.data['type']}


            return turns_data

        except KeyError as e:
            raise IncompleteDataException400(e)

    elif table_name == 'matches':

        try:
            matches_data = {'status': request.data['status'],
                            'time': request.data['time'],
                            'datetime': request.data['datetime'],
                            'date_unix': request.data['date_unix'],
                            'score': request.data['score']}

            return matches_data


        except KeyError as e:

            raise IncompleteDataException400(e)

    elif table_name == 'players':

        try:
            players_data = {'name': request.data['name'],
                            'icon': request.data['icon'],
                            'number': request.data['number'],
                            'url': request.data['url'],
                            'position': request.data['position'].lower(),
                            'birthday': request.data['birthday'],
                            'country': request.data['country'],
                            'command': request.data['command'],
                            'cost': request.data['cost']}

            return players_data


        except KeyError as e:

            raise IncompleteDataException400(e)

    raise WrongTableException400