import csv
import chardet
from django.core.management.base import BaseCommand
from players.models import League, Team, Player

class Command(BaseCommand):
    help = 'Import players from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
            default='/home/tl/Documents/prem_players_final.csv',
            help='Path to the CSV file (default: %(default)s)')
        parser.add_argument('--league', type=str, required=True,
            help='Name of the league')
        parser.add_argument('--country-code', type=str, required=True,
            help='ISO 3166-1 alpha-3 country code')
        parser.add_argument('--tier', type=int, default=1,
            help='League tier (default: 1)')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        league_name = options['league']
        country_code = options['country_code'].upper()
        tier = options['tier']

        # Create or get the league
        league, created = League.objects.get_or_create(
            name=league_name,
            country_code=country_code,
            tier=tier
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created league: {league.name} ({league.country_code}{league.tier})'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Using existing league: {league.name} ({league.country_code}{league.tier})'))

        with open(csv_file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            file_encoding = result['encoding']

        self.stdout.write(self.style.SUCCESS(f'Detected file encoding: {file_encoding}'))

        
        with open(csv_file_path, 'r', encoding=file_encoding) as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    # Get or create the team
                    team, _ = Team.objects.get_or_create(
                        name=row['club'],
                        defaults={'league': league}  # Associate team with league
                    )
                    # Process each row and create Player objects
                    player, created = Player.objects.get_or_create(
                        first_name=row['first_name'],
                        last_name=row['last_name'],
                        defaults={
                            'nationality': row['nationality'],
                            'age': int(row['age']) if row['age'].isdigit() else None,
                            'shirt_number': int(row['shirt_number']) if row['shirt_number'].isdigit() else None,
                            'position': row['position'],
                            'team': team,
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Created player: {player}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Player already exists: {player}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing row: {row}. Error: {str(e)}'))
        self.stdout.write(self.style.SUCCESS('Player import completed'))