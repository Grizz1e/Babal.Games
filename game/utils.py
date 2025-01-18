from .models import GameOrder, GameVoucher, Game, GameReview
from django.db.models import Count, Q, F, Avg, ExpressionWrapper, FloatField, Case, When
from django.db.models.functions import Cast
from django.contrib.auth import get_user_model
from collections import Counter

def voucher_applicable(voucher: GameVoucher, order: GameOrder, request):
    if request.user in voucher.used_by.all():
        print('Voucher already used')
        return False
    
    if order.total_price < voucher.minimum_spend:
        print('Minimum spend not reached')
        return False
    
    print('Applicable')
    return True

from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta

def get_weekly_revenue():
    # Get today's date and the date 7 days ago
    today = timezone.now()
    last_week = today - timedelta(days=7)

    # Query orders created within the last week
    orders = GameOrder.objects.filter(order_date__gte=last_week)

    # Aggregate total revenue for each day
    revenue_data = orders.values('order_date__date').annotate(
        daily_revenue=Sum('total_price') - Sum('voucher_amount')
    ).order_by('order_date__date')

    # Prepare data for Chart.js
    labels = []
    revenue = []
    for entry in revenue_data:
        labels.append(entry['order_date__date'].strftime('%b %d'))
        revenue.append(entry['daily_revenue'] or 0)  # In case no revenue for a day

    # For the next 7 days, fill in missing data
    for i in range(7):
        day = today - timedelta(days=i)
        day_str = day.strftime('%b %d')
        if day_str not in labels:
            labels.append(day_str)
            revenue.append(0)

    # Reverse the order for the chart (so the first day is on the left)
    labels.reverse()
    revenue.reverse()

    return labels, revenue


class GameRecommendationService:
    def __init__(self, user=None):
        self.user = user
        self.User = get_user_model()
        self.is_authenticated = user is not None and user.is_authenticated
    
    def get_similar_games(self, game:Game, limit:int=5):
        return Game.objects.filter(
            genre__in=game.genre.all()
        ).exclude(id=game.id).distinct()[:limit]

    def get_user_genre_preferences(self):
        """Calculate genre preferences based on user's purchase history."""
        if not self.is_authenticated:
            return Counter()

        user_games = Game.objects.filter(
            gameorder__buyer=self.user,
            gameorder__status=2  # Completed orders only
        ).distinct()
        
        genre_counts = Counter()
        for game in user_games:
            genres = game.genre.all()
            for genre in genres:
                genre_counts[genre.id] += 1
                
        return genre_counts

    def get_similar_users(self, min_common_games=2):
        """Find users with similar gaming preferences."""
        if not self.is_authenticated:
            return self.User.objects.none()

        user_games = Game.objects.filter(
            gameorder__buyer=self.user,
            gameorder__status=2
        ).distinct()

        similar_users = self.User.objects.filter(
            gameorder__games__in=user_games,
            gameorder__status=2
        ).exclude(id=self.user.id).annotate(
            common_games=Count('gameorder__games', 
            filter=Q(gameorder__games__in=user_games))
        ).filter(common_games__gte=min_common_games)

        return similar_users
    
    def get_top_rated_games(self, limit:int=6, min_number_of_rating:int=10):

        # Calculate the mean of average ratings (C)
        all_games = Game.objects.annotate(
            total_ratings=(
                F('gamerating__five_stars') +
                F('gamerating__four_stars') +
                F('gamerating__three_stars') +
                F('gamerating__two_stars') +
                F('gamerating__one_stars')
            ),
            total_score=(
                5 * F('gamerating__five_stars') +
                4 * F('gamerating__four_stars') +
                3 * F('gamerating__three_stars') +
                2 * F('gamerating__two_stars') +
                1 * F('gamerating__one_stars')
            ),
            average_rating=Case(
                When(total_ratings=0, then=0),
                default=F('total_score') / F('total_ratings'),
                output_field=FloatField()
            )
        )

        # Calculate C (mean average rating)
        total_ratings_count = all_games.aggregate(total=Sum('total_ratings'))['total']
        total_average_rating = all_games.aggregate(total=Sum('total_score'))['total']
        C = total_average_rating / total_ratings_count if total_ratings_count else 0

        # Annotate games with weighted score
        top_rated_games = all_games.annotate(
            weighted_score=(
                (F('total_ratings') * F('average_rating') + min_number_of_rating * C) / (F('total_ratings') + min_number_of_rating)
            )
        ).order_by('-weighted_score')[:limit]  # Limit to top 5 games

        return top_rated_games


    # def get_top_rated_games(self, limit=6, min_reviews=0):
    #     """Get top rated games using a weighted scoring system."""
    #     # First, get the mean rating across all games with minimum reviews
    #     overall_mean = Game.objects.annotate(
    #         review_count=Count('reviews'),
    #         avg_rating=Avg('reviews__rating')
    #     ).filter(
    #         review_count__gte=min_reviews
    #     ).aggregate(
    #         mean=Avg('avg_rating')
    #     )['mean'] or 0

    #     dampening_factor = float(min_reviews) * 2

    #     top_games = Game.objects.annotate(
    #         review_count=Count('reviews'),
    #         avg_rating=Avg('reviews__rating')
    #     ).filter(
    #         review_count__gte=min_reviews
    #     ).annotate(
    #         weighted_rating=ExpressionWrapper(
    #             (Cast('review_count', FloatField()) / (Cast('review_count', FloatField()) + dampening_factor) * Cast('avg_rating', FloatField())) +
    #             (dampening_factor / (Cast('review_count', FloatField()) + dampening_factor) * overall_mean),
    #             output_field=FloatField()
    #         )
    #     ).order_by('-weighted_rating')[:limit]

    #     return top_games

    def get_top_selling_games(self):
        # Step 1: Filter GameOrders that are completed
        completed_orders = GameOrder.objects.filter(status=2)
        
        # Step 2: If there are completed orders, count the sales of each game
        if completed_orders.exists():
            game_sales = completed_orders.values('games').annotate(sales_count=Count('games')).order_by('-sales_count')
            
            # Step 3: Collect top-selling games from the completed orders
            top_selling_games = []
            for entry in game_sales:
                game = Game.objects.get(id=entry['games'])
                sales_count = entry['sales_count']
                top_selling_games.append(game)
            
            # If there are fewer than 6 games, fill in the remaining spots from the default order
            if len(top_selling_games) < 6:
                remaining_count = 6 - len(top_selling_games)
                # Get remaining games from the default order, making sure they are not duplicates
                default_games = Game.objects.all()[:remaining_count]  # Get remaining games
                for game in default_games:
                    # Only append the game if it's not already in the list
                    if game not in top_selling_games:
                        top_selling_games.append(game)
                
                # If there are still not enough games, continue appending until we reach 6
                if len(top_selling_games) < 6:
                    # Get additional games and ensure they are not duplicates
                    all_default_games = Game.objects.all()  # Get all games if needed
                    for game in all_default_games:
                        if len(top_selling_games) >= 6:
                            break
                        if game not in top_selling_games:
                            top_selling_games.append(game)

            return top_selling_games
        
        # Step 4: If there are no completed orders, recommend at least 6 games based on default order
        default_games = Game.objects.all()[:6]  # Get top 6 games from default order
        
        # Return 6 games with sales count set to 0 (since no sales data is available)
        top_selling_games = [game for game in default_games]
        
        return top_selling_games


    def get_recommendations(self, limit=10):
        """Get personalized game recommendations."""
        if not self.is_authenticated:
            return self.get_top_rated_games(limit=limit)

        genre_preferences = self.get_user_genre_preferences()
        similar_users = self.get_similar_users()

        user_purchased_games = Game.objects.filter(
            gameorder__buyer=self.user,
            gameorder__status=2
        )
        
        recommendations = Game.objects.exclude(
            id__in=user_purchased_games
        ).annotate(
            # Calculate the number of related genres that match the user's genre preferences
            genre_count=Count('genre', filter=Q(genre__id__in=genre_preferences.keys())),

            # Calculate how many orders are associated with the game, indicating copies sold
            copies_sold=Count('gameorder'),

            # Calculate the average user rating based on reviews
            user_rating=Avg('reviews__rating'),

            # Combine all the factors into a score
            score=F('genre_count') +
                F('copies_sold') / 1000.0 +  # Optional scaling factor for copies sold
                F('user_rating')
        ).order_by('-score')[:limit]

        return recommendations

    def get_for_you_games(self, limit=6):
        """Get personalized recommendations or top-rated games for anonymous users."""
        if not self.is_authenticated:
            return self.get_top_rated_games(limit=limit)

        # Get personalized recommendations
        personalized_recs = self.get_recommendations(limit=limit)
        recommended_games = list(personalized_recs)

        # If we don't have enough recommendations, add top-rated games
        if len(recommended_games) < limit:
            # Get user's already purchased games
            user_purchased_games = Game.objects.filter(
                gameorder__buyer=self.user,
                gameorder__status=2
            )
            
            # Get all games to exclude (recommendations + purchased)
            exclude_ids = list(user_purchased_games.values_list('id', flat=True))
            exclude_ids.extend(game.id for game in recommended_games)

            # Get top rated games excluding ones we already have
            needed_games = limit - len(recommended_games)
            top_rated = Game.objects.exclude(
                id__in=exclude_ids
            ).annotate(
                review_count=Count('reviews'),
                avg_rating=Avg('reviews__rating')
            ).filter(
                review_count__gte=3
            ).annotate(
                weighted_rating=ExpressionWrapper(
                    (
                        Cast('review_count', FloatField()) / (Cast('review_count', FloatField()) + 6) * Cast('avg_rating', FloatField())
                    ) + (
                        6 / (Cast('review_count', FloatField()) + 6) * (
                            Game.objects.filter(id__in=GameReview.objects.values('game'))  # Ensure we are considering games with reviews
                            .aggregate(mean=Avg('reviews__rating'))['mean'] or 0
                        )
                    ),
                    output_field=FloatField()
                )
            ).order_by('-weighted_rating')[:needed_games]

            recommended_games.extend(list(top_rated))

        return recommended_games