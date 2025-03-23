
public class TihaiGenerator
{
	public static String tihai;
	public static String tertile[];
	public static int lengthOfTertile;
	public static int indexOfSamm;
	public static int currentSubbeat;
	public static int count;
	public static int subBeatsRemaining;

	public static void selectTihai(int subBeats)
	{
		for(int i=1;i<16;i++)
			generateTihais(i, subBeats);		
	}

	public static void generateTihais(int beats, int subBeats)
	{
		currentSubbeat=0;
		tihai = "";
		tertile=new String[100];

		subBeatsRemaining=(beats*subBeats)+1;
		subBeatsRemaining=nearestGreaterMultipleOf(subBeatsRemaining, 3);

		lengthOfTertile = subBeatsRemaining/3;
		indexOfSamm=(lengthOfTertile-(subBeatsRemaining-((beats*subBeats)+1)))-1;
/*		
		System.out.println("subBeatsRemaining: "+subBeatsRemaining);
		System.out.println("lengthOfTertile: "+lengthOfTertile);
		System.out.println("indexOfSamm: "+indexOfSamm);
		
*/		count=0;
		if(indexOfSamm>=0)
		{
			while(currentSubbeat<lengthOfTertile)
			{
				if(currentSubbeat==indexOfSamm)
					tertile[currentSubbeat]="Dha";
				else
					tertile[currentSubbeat]=String.valueOf(++count);
				currentSubbeat++;
			}
		}
		/*		
		if(indexOfSamm>=0)
		{
		System.out.println("Tertile : ");
		for(int i=0;i<tertile.length;i++)
		{
			if(tertile[i]!=null)
			System.out.print(tertile[i]);
		}
		System.out.println("\n");
		}
		*/
		currentSubbeat=0;
		count=0;
		if(indexOfSamm>=0)
		{
			while(currentSubbeat<subBeatsRemaining)
			{
				if(currentSubbeat>=((beats*subBeats)+1))
				{
					currentSubbeat++;
					continue;
				}

				if(currentSubbeat%subBeats==0 && currentSubbeat!=0)
					tihai+="\t";
				tihai+=tertile[count];
				//System.out.println("subbeat "+i+" has"+tertile[count]);
				currentSubbeat++;
				count=count+1;
				count=count%lengthOfTertile;
			}
			System.out.println("\nBeats : "+beats+" Tertile length : "+lengthOfTertile);
			tokenizeTihai(tihai);
		}
	}

	public static void tokenizeTihai(String originalTihai)
	{
		String tokenizedTihai=originalTihai;
		System.out.println(tokenizedTihai);
	}

	public static int nearestGreaterMultipleOf(int i, int j)
	{
		if(i%j==0)
			return i;
		else if(i%j==1)
			return (i+2);
		else
			return (i+1);
	}

	public static void main(String[] args)
	{
		for(int i=1;i<=8;i++)
		{
			System.out.println("Sub Beats Per Beat : "+i+"");
			selectTihai(i);
		}
		//generateTihais(2, 1);
	}
}
