with open('example_config.txt', 'w') as f:
    for i in range(1, 11):
        f.write('00-00-00-00-00-00-00-{:02},420{:02}\n'.format(i, i))
